class Config(object):
    DEBUG = False
    TESTING = False


class Development(Config):
    DEBUG = True
    NODES = ['192.168.40.11']
    KEYSPACE = 'whatsup_development'


class Test(Config):
    DEBUG = True
    TESTING = True
    NODES = ['192.168.40.11']
    KEYSPACE = 'whatsup_test'


class Production(Config):
    NODES = ['127.0.0.1']
    KEYSPACE = 'whatsup_production'
