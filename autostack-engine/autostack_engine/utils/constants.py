TECHNOLOGY_CATALOG = {
    # Runtimes
    "nodejs": {"category": "runtime", "versions": ["18", "20", "22"], "nix_package": "nodejs"},
    "python": {"category": "runtime", "versions": ["3.9", "3.10", "3.11", "3.12", "latest"], "nix_package": "python3"},
    "java": {"category": "runtime", "versions": ["11", "17", "21", "latest"], "nix_package": "openjdk"},
    "go": {"category": "runtime", "versions": ["1.20", "1.21", "1.22", "latest"], "nix_package": "go"},
    
    # Databases
    "postgresql": {"category": "database", "versions": ["14", "15", "16", "latest"], "nix_package": "postgresql"},
    "mysql": {"category": "database", "versions": ["8.0", "8.1", "latest"], "nix_package": "mysql80"},
    "mongodb": {"category": "database", "versions": ["6.0", "7.0", "latest"], "nix_package": "mongodb"},
    "sqlite": {"category": "database", "versions": ["3", "latest"], "nix_package": "sqlite"},
    
    # Cache
    "redis": {"category": "cache", "versions": ["6", "7", "latest"], "nix_package": "redis"},
    "memcached": {"category": "cache", "versions": ["1.6", "latest"], "nix_package": "memcached"},
    
    # Queues
    "rabbitmq": {"category": "queue", "versions": ["3.12", "latest"], "nix_package": "rabbitmq-server"},
    "kafka": {"category": "queue", "versions": ["2.8", "latest"], "nix_package": "apache-kafka"},
}
