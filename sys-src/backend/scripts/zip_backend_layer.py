import shutil
from os.path import dirname, realpath

dir_path = dirname(dirname(realpath(__file__)))
zip_source_dir = dir_path + "/requirements"
zip_target_file = dir_path + "/lambda_layers/backend_lambda_layer"
shutil.make_archive(zip_target_file, "zip", zip_source_dir)
