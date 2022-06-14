--
-- Database schema for Tenyks Challenge
--

CREATE SCHEMA IF NOT EXISTS tenyks;
SET search_path TO tenyks;

CREATE TABLE IF NOT EXISTS dataset_type(
    id INT GENERATED BY DEFAULT AS IDENTITY,
    name VARCHAR(64) NOT NULL,
    PRIMARY KEY (id)
);

INSERT INTO dataset_type (id, name)
VALUES
    (1, 'jpeg'),
    (2, 'jpg'),
    (3, 'png'),
    (4, 'gif'),
    (5, 'tiff'),
    (6, 'bmp'),
    (7, 'svg')
ON CONFLICT (id) DO NOTHING;

CREATE TABLE IF NOT EXISTS dataset (
    id INT GENERATED BY DEFAULT AS IDENTITY,
    dataset_type_id INT NOT NULL,
    dataset_name VARCHAR(64) NOT NULL,
    dataset_size INT NOT NULL,
    dataset_path VARCHAR(1024) NOT NULL,
    images_path VARCHAR(1024) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (dataset_name, dataset_path),
    CONSTRAINT fk_tenyks_dataset_dataset_type FOREIGN KEY (dataset_type_id) REFERENCES dataset_type(id)
);

CREATE TABLE IF NOT EXISTS model(
    id INT GENERATED BY DEFAULT AS IDENTITY,
    name VARCHAR(64) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE(name)
);

CREATE TABLE IF NOT EXISTS model_dataset(
    model_id INT NOT NULL,
    dataset_id INT NOT NULL,
    PRIMARY KEY (model_id, dataset_id),
    CONSTRAINT fk_tenyks_model_dataset_dataset FOREIGN KEY (dataset_id) REFERENCES dataset(id),
    CONSTRAINT fk_tenyks_model_dataset_model FOREIGN KEY (model_id) REFERENCES model(id)
);

CREATE TABLE IF NOT EXISTS image(
    id INT GENERATED BY DEFAULT AS IDENTITY,
    dataset_id INT NOT NULL,
    name VARCHAR(128) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE(name),
    CONSTRAINT fk_tenyks_image_dataset FOREIGN KEY (dataset_id) REFERENCES dataset(id)
);

CREATE TABLE IF NOT EXISTS image_category(
    id INT GENERATED BY DEFAULT AS IDENTITY,
    category INT NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS image_bbox(
    id INT GENERATED BY DEFAULT AS IDENTITY,
    image_id INT NOT NULL,
    category_id INT NOT NULL,
    bbox_json JSON NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_tenyks_image_bbox_image FOREIGN KEY (image_id) REFERENCES image(id),
    CONSTRAINT fk_tenyks_image_bbox_image_category FOREIGN KEY (category_id) REFERENCES image_category(id)
);

CREATE TABLE IF NOT EXISTS model_image_category(
    id INT GENERATED BY DEFAULT AS IDENTITY,
    category INT NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS model_image_bbox(
    id INT GENERATED BY DEFAULT AS IDENTITY,
    image_id INT NOT NULL,
    model_id INT NOT NULL,
    category_id INT NOT NULL,
    bbox_json JSON NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_tenyks_model_image_bbox_image FOREIGN KEY (image_id) REFERENCES image(id),
    CONSTRAINT fk_tenyks_model_image_bbox_image_category FOREIGN KEY (category_id) REFERENCES model_image_category(id)
);

CREATE TABLE IF NOT EXISTS model_image_heatmap(
    image_id INT NOT NULL,
    model_id INT NOT NULL, 
    result_path VARCHAR(1024) NOT NULL,
    PRIMARY KEY (image_id, model_id),
    CONSTRAINT fk_tenyks_model_image_heatmap_image FOREIGN KEY (image_id) REFERENCES image(id),
    CONSTRAINT fk_tenyks_model_image_heatmap_model FOREIGN KEY (model_id) REFERENCES model(id)
);

CREATE TABLE IF NOT EXISTS model_image_activations(
    image_id INT NOT NULL,
    model_id INT NOT NULL, 
    result_path VARCHAR(1024) NOT NULL,
    PRIMARY KEY (image_id, model_id),
    CONSTRAINT fk_tenyks_model_image_activations_image FOREIGN KEY (image_id) REFERENCES image(id),
    CONSTRAINT fk_tenyks_model_image_activations_model FOREIGN KEY (model_id) REFERENCES model(id)
);
