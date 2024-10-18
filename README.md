# KDA Module Processor

![KDA Logo](https://www.kadena.io/favicon.ico)

**KDA Module Fetcher** is a versatile and automated tool designed to streamline the process of fetching and organizing KDA (Kadena) smart contract modules. This script fetches every module that is deployed on a given chain under a given namespace.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Dynamic Configuration:** Substitute placeholders in YAML templates with user-provided values.
- **Automated JSON Generation:** Utilize the `kda gen` command to generate JSON configurations.
- **Module Fetching:** Execute `kda local` to retrieve KDA module data based on the generated JSON.
- **Organized Output:** Parse the JSON output and create structured `.pact` files within namespace-specific directories.
- **Flexible Usage:** Fetch modules from any chain and any namespace. It is configured for testnet by default but can easily be used in other networks as well

## Prerequisites

Before using the **KDA Module Fetcher**, ensure you have the following installed and configured on your system:

- **Python 3.7+**
  - Verify installation:
    ```sh
    python3 --version
    ```
- **KDA Tool (`kda-tool`)**
  - Installation instructions can be found [here](https://github.com/kadena-io/kda-tool).
  - Ensure `kda-tool` is accessible in your system's PATH.

- **Git** (for cloning the repository)
  - Verify installation:
    ```sh
    git --version
    ```

## Installation

1. **Clone the Repository:**

   ```sh
   git clone https://github.com/yourusername/kda-module-fetcher.git
   cd kda-module-fetcher
   ```

Make the Script Executable:

```sh
   
   chmod +x fetch_namespace_modules.py

```



# Usage

Basic Usage with Default Arguments:


``` sh

./fetch_namespace_modules.py

```


This command uses the default network URL (https://testnet.mindsend.xyz), chain (0), and namespace (n_9b079bebc8a0d688e4b2f4279a114148d6760edf).

Specify a Different Chain and Namespace:

``` sh

./fetch_namespace_modules.py --chain "1" --namespace "n_abcdef123456"

```

# How It Works

### Placeholder Substitution: 
The script reads a YAML template file (fetch-modules.ktpl by default) containing placeholders like {{{chain}}} and {{{namespace}}}. These placeholders are dynamically replaced with the values provided via command-line arguments.

### JSON Generation:
        
  Using the substituted YAML file, the script executes the kda gen command to generate a corresponding JSON configuration file (temp_fetch_module_code.json).

### Fetching Module Data:
  
  The script then runs the kda local command with the generated JSON and specified network URL to retrieve module information.

### Parsing and File Creation:
  
  The JSON output from kda local is parsed to extract each module's name and code.   

### Cleanup:
        
  Temporary files (substituted_config.ktpl and temp_fetch_module_code.json) are deleted after processing to maintain a clean workspace.


# Contributing

This repo welcomes forks, PRs and issues !

# License

This project is licensed under the MIT License.
