# DecoyHive

DecoyHive is a honeypot generator toolkit designed to analyze a target system and create a near-exact clone using containerized or VM-based deployment. It consists of two main components:

1. **Analyzer** – Gathers information about the target system, including hardware, operating system, network settings, and running services, then generates a configuration file.
2. **Generator** – Uses the generated configuration file to create a decoy environment that mimics the target system, helping detect and divert unauthorized access attempts.

## Features
- **System Analysis:** Extracts key system details, including OS information, network configuration, and active services.
- **Config-based Cloning:** Uses an automatically generated config file to create an accurate honeypot environment.
- **Containerized & VM Support:** Initial implementation focuses on Docker/Kubernetes-based deployment, with potential expansion to VM-based replication.
- **Intrusion Response:** Can integrate with IDS to automatically switch traffic to the honeypot upon detecting suspicious activity.

## Installation
### Prerequisites
- Python 3.11+
- Docker (for containerized honeypot deployment)
- Root privileges (for system analysis and network scanning)

### Clone the Repository
```sh
git clone https://github.com/ForeverKnight1455/DecoyHive.git
cd DecoyHive
```


## Usage
### Running the Analyzer
The analyzer extracts system details and generates a configuration file.
```sh
python analyzer/__main__.py
```
This will create `config_exports/config.json`, which is used for generating the honeypot.


## Project Structure
```
DecoyHive/
├── analyzer/            # System analysis component
│   ├── __main__.py      # Entry point for system analysis
│   ├── utils/           # Utility scripts for gathering info
│   │   ├── hw_info.py   # Hardware details
│   │   ├── net_info.py  # Network configuration
│   │   ├── os_info.py   # OS and system details
│   │   ├── software_info.py # Running services & installed software
├── config_exports/      # Stores generated configuration files
│   └── config.json      # Sample output config
├── honeypot.log         # Logging system events
├── settings.json        # Configuration settings
├── README.md            # Project documentation
```

## Roadmap
- [x] System analysis module
- [ ] Honeypot deployment using Docker
- [ ] IDS integration for real-time monitoring
- [ ] VM-based honeypot support

## Contributing
Contributions are welcome! Feel free to open an issue or submit a pull request.

## License
This project is licensed under the MIT License.
