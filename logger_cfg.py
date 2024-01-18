logger_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'std_format': {
            'format': '{asctime} {message}',
            'style': '{'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'std_format'
        },
        'logfile': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'filename': 'debug.log',
            'encoding': 'utf-8',
            'mode': 'a',
            'formatter': 'std_format'
        }
    },
    'loggers': {
        'logger': {
            'level': 'DEBUG',
            'handlers': [
                'console', 'logfile'
            ]
            # 'propagate': False
        }
    },
    'filters': {},
    'root': {}
}
