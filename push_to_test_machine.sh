#!/bin/sh

rsync -r html/ hdip_proj@192.168.122.110:/var/www/html
rsync -r python_code/ hdip_proj@192.168.122.110:/home/hdip_proj/server_scripts
rsync -r php_code/ hdip_proj@192.168.122.110:/home/hdip_proj/server_php_code
rsync -r database/ hdip_proj@192.168.122.110:/home/hdip_proj/db_scripts
rsync -r project_data_files/ hdip_proj@192.168.122.110:/home/hdip_proj/project_data_files

rsync -a config.ini hdip_proj@192.168.122.110:/home/hdip_proj/config.ini
