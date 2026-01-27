class Config:
    SECRET_KEY = "clave-secreta-ambato"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost/transporte"
    SQLALCHEMY_TRACK_MODIFICATIONS = False