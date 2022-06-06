import asyncio
from functools import wraps
from typing import Optional, Dict, List, Tuple, Union, Callable
from importlib.metadata import version
from starlette.concurrency import run_in_threadpool
import anyio.lowlevel
import cv2
import numpy as np


CapacityLimiter = anyio.lowlevel.get_asynclib("asyncio").CapacityLimiter

concurrent_limiter = CapacityLimiter(1)


def run_serialised_in_worker(func: Callable):
    @wraps(func)
    async def wrapped(*args, **kwargs):
        async with concurrent_limiter:
            return await run_in_threadpool(func, *args, **kwargs)
    return wrapped


serialised_decode = run_serialised_in_worker(cv2.imdecode)


class StudyEvaluatorAdapter:
    """
    Wraps the study evaluator from tech recall library in order to adapt the handler input and output to the library
    """

    def __init__(self, config: ConfigRegion) -> None:
        if config == ConfigRegion.EU:
            evaluation_type = "LRCB"
        elif config == ConfigRegion.US:
            evaluation_type = "US"

        self.study_evaluator = StudyEvaluator(evaluation_type=evaluation_type)

    @run_serialised_in_worker
    def _image_features_and_svg(
        self, image_pixels: np.array, image_input: ImageInput
    ) -> Tuple[Union[CCGeometryFeatures, MLOGeometryFeatures], SVG]:
        px_spacing = image_input.image_properties.pixelSpacing or image_input.image_properties.imagerPixelSpacing

        if image_input.image_properties.view == View.CC:
            features, svgs = self.study_evaluator.get_image_features_and_svgs(
                image_pixels=image_pixels,
                spacing=px_spacing.as_array,
                view="CC",
            )
        elif image_input.image_properties.view == View.MLO:
            features, svgs = self.study_evaluator.get_image_features_and_svgs(
                image_pixels=image_pixels,
                spacing=px_spacing.as_array,
                view="MLO",
            )

        return features, svgs

    async def _case_features_and_svgs(
        self, study: List[ ImageInput]
    ) -> Tuple[CaseGeometryFeatures, Dict[LateralityView, SVG]]:
        # Segmentation and geometric features extraction
        case_features = CaseGeometryFeatures()
        svgs: Dict[LateralityView, SVG] = {}

        async def get_for_single_image(image_input):
            image_properties = image_input.image_properties
            image_data = await image_input.png_data.read()
            image = await serialised_decode(
                np.frombuffer(image_data, np.uint8),
                cv2.IMREAD_ANYDEPTH | cv2.IMREAD_GRAYSCALE,
            )

            features, svg = await self._image_features_and_svg(image, image_input)
            case_features.add(image_properties.view.value, image_properties.laterality.value, features)
            svgs[LateralityView.create(image_properties.laterality, image_properties.view)] = svg

        await asyncio.gather(*(get_for_single_image(image_input) for image_input in study))

        return case_features, svgs

    def _classification_from_features(
        self, features: Union[MLOGeometryFeatures, CCGeometryFeatures]
    ) -> ImageAdequacy:
        prediction = self.study_evaluator.get_classification_from_features(
            features=features
        )

        return {
            "Adequate Image": ImageAdequacy.Adequate,
            "Inadequate Image": ImageAdequacy.Inadequate,
            "Image for Review": ImageAdequacy.Indeterminate,
        }[prediction.classification]

    def _criteria_from_case_features(
        self, features: Union[MLOGeometryFeatures, CCGeometryFeatures]
    ) -> Dict[Criterion, CriterionAdequacy]:
        criteria = self.study_evaluator.get_criteria_from_case_features(
            features=features
        )

        criteria_results: Dict[Criterion, CriterionAdequacy] = {}

        for criterion in criteria:
            criteria_results[Criterion(criterion.name)] = CriterionAdequacy.from_bool(
                criterion.sub_optimal_result
            )

        return criteria_results

    @run_serialised_in_worker
    def _generate_image_output(
        self,
        image_input: ImageInput,
        case_features: CaseGeometryFeatures,
        breast_size: BreastSize,
        output_svg: Blob,
    ):
        return ImageEvaluation(
            image_properties= image_input.image_properties,
            fullsize= image_input.png_data,
            thumb= image_input.png_data,
            svg=output_svg,
            adequacy=self._classification_from_features(
                getattr(
                    getattr(case_features, image_input.image_properties.laterality.value),
                    image_input.image_properties.view.value,
                ),
            ),
            assessment=self._criteria_from_case_features(
                getattr(
                    getattr(case_features, image_input.image_properties.laterality.value),
                    image_input.image_properties.view.value,
                ),
            ),
            breast_size=breast_size,
        )

    def _generate_default_review_result(self, study: List[ImageInput]):
        output_study: List[ImageEvaluation] = []
        for image_input in study:
            criteria_results: Dict[Criterion, CriterionAdequacy] = {}

            if image_input.image_properties.view == View.CC:
                criterion_list = self.study_evaluator.get_criterion_names(view="CC")
            elif image_input.image_properties.view == View.MLO:
                criterion_list = self.study_evaluator.get_criterion_names(view="MLO")

            for criterion_name in criterion_list:
                criteria_results[
                    Criterion(criterion_name)
                ] = CriterionAdequacy.Inadequate

            image_output = ImageEvaluation(
                image_properties=image_input.image_properties,
                fullsize=image_input.png_data,
                thumb=image_input.png_data,
                svg=None,
                adequacy=ImageAdequacy.Indeterminate,
                assessment=criteria_results,
                breast_size=None,
            )
            output_study.append(image_output)
        return output_study

    def _estimate_breast_size(self, case_features: CaseGeometryFeatures) -> BreastSize:
        "Estimate breast size from visible breast area on MLO views"
        SMALL_BREAST_THRESHOLD = 17559.959725
        LARGE_BREAST_THRESHOLD = 25757.155638
        if case_features.L.MLO is not None and case_features.R.MLO is not None:
            avg_breast_area = (
                case_features.L.MLO.breast_area + case_features.R.MLO.breast_area
            ) / 2
        elif case_features.L.MLO is not None:
            avg_breast_area = case_features.L.MLO.breast_area
        elif case_features.R.MLO is not None:
            avg_breast_area = case_features.R.MLO.breast_area
        else:
            # TODO: None or fixed value in this case?
            return BreastSize.Indeterminate

        if avg_breast_area < SMALL_BREAST_THRESHOLD:
            breast_size = BreastSize.Small
        elif (
            SMALL_BREAST_THRESHOLD < avg_breast_area
            and avg_breast_area < LARGE_BREAST_THRESHOLD
        ):
            breast_size = BreastSize.Medium
        elif avg_breast_area > LARGE_BREAST_THRESHOLD:
            breast_size = BreastSize.Large
        return breast_size

    async def evaluate(
        self,
        study: List[ImageInput],
        prior_study: Optional[List[ImageInput]] = None,
    ) -> List[ImageEvaluation]:
        try:
            case_features, svgs = await self._case_features_and_svgs(study=study)

            # Cross populate the features
            await run_serialised_in_worker(case_features.cross_populate)()

            if prior_study:
                prior_case_features, _ = await self._case_features_and_svgs(
                    study=prior_study
                )

                # Add the priors and cross populate them
                prior_case_features.cross_populate()
                case_features.add_priors(prior_case_features)

            breast_size = self._estimate_breast_size(case_features)

            async def evaluate_image(image_input):
                output_svg = await image_input.png_data.cocreate(
                    f"{image_input.image_properties.sopInstanceUID}-TR-{version('tech_recall')}.svg", mimeType="image/svg+xml"
                )
                await output_svg.write(str(svgs[LateralityView.create(image_input.image_properties.laterality,image_input.image_properties.view)]).encode("utf-8"))

                return await self._generate_image_output(
                    image_input,
                    case_features,
                    breast_size,
                    output_svg,
                )

            output_study = await asyncio.gather(*(evaluate_image(image_input) for image_input in study))

        # TODO: AttributeError might be too broad best would be to get specific except from tech recall package,
        # when crucial parts of breast could not be detected
        except AttributeError as e:
            if str(e) == "Case features are not valid":
                print(f"Attribute error: {e}")
                output_study = self._generate_default_review_result(study=study)
            else:
                raise

        return output_study


evaluators: Dict[ConfigRegion, StudyEvaluatorAdapter] = {
    ConfigRegion.EU: StudyEvaluatorAdapter(ConfigRegion.EU),
    ConfigRegion.US: StudyEvaluatorAdapter(ConfigRegion.US),
}


async def process(request: Request) -> Response:
    model = Model.fromVersionString(name=request.config, version=version("tech_recall"))
    if len(request.study or []) > 4 or len(request.prior_study or []) > 4:
        raise ValueError(f"Prior and latest studies should have 4 or less images.")
    wrapper = evaluators[request.config]
    study = [
        ImageInput(
            png_data=i.target.png,
            image_properties=i.properties,

        )
        for i in request.study
    ]
    prior_study = [
        ImageInput(png_data=i.target.png, image_properties=i.properties)
        for i in request.prior_study or []
    ]
    output_study = await wrapper.evaluate(study=study, prior_study=prior_study)
    
    for image_eval in output_study:
        if image_eval.adequacy == None:
            raise ValueError(f"Latest study image evaluation with StudyUID/SopUID: \
                {image_eval.image_properties.studyInstanceUID}/{image_eval.image_properties.sopInstanceUID} is missing adequacy")
        if image_eval.assessment == None:
            raise ValueError(f"Latest study image evaluation with StudyUID/SopUID: \
                {image_eval.image_properties.studyInstanceUID}/{image_eval.image_properties.sopInstanceUID} is missing assessment")
     
    # Convert to slightly different type - TODO: Needs better thinking, some replication present here
    prior_study = [
        ImageEvaluation(
            image_properties=i.image_properties,
            fullsize=i.png_data,
            thumb=i.png_data
        ) for i in prior_study or []
    ]
    
    evaluation = PriorLatestPair(evaluation_model=model, latest=output_study, prior=prior_study)
 
    return Response(evaluation=evaluation)
