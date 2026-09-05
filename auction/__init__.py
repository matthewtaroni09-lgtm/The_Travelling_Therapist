import pymysql
pymysql.install_as_MySQLdb()

from django.db.backends.mysql.features import DatabaseFeatures
DatabaseFeatures.minimum_database_version = (8, 0, 0)