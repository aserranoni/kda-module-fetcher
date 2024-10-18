#!/usr/bin/env python3

import argparse
import asyncio
import sys
import os
import json
import re


async def run_command(command, cwd=None):
    """
    Asynchronously run a shell command and capture its output.
    """
    process = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=cwd
    )
    stdout, stderr = await process.communicate()
    return process.returncode, stdout.decode(), stderr.decode()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Process KDA Module Code with Dynamic Configuration."
    )
    parser.add_argument(
        "-n",
        "--network_url",
        default="https://testnet.mindsend.xyz",
        help="Network URL to use (default: https://testnet.mindsend.xyz)",
    )
    parser.add_argument(
        "--chain",
        default="0",
        help="Value to substitute for {{{chain}}} in the YAML template",
    )
    parser.add_argument(
        "--namespace",
        default="n_9b079bebc8a0d688e4b2f4279a114148d6760edf",
        help="Value to substitute for {{{namespace}}} in the YAML template",
    )
    return parser.parse_args()


def substitute_placeholders(template_content, substitutions):
    """
    Replace placeholders in the template with actual values.
    Placeholders are in the form {{{placeholder}}}.
    """

    def replacer(match):
        key = match.group(1)
        return substitutions.get(
            key, match.group(0)
        )  # Leave unchanged if key not found

    pattern = re.compile(r"\{\{\{(\w+)\}\}\}")
    return pattern.sub(replacer, template_content)


async def generate_json(template_path, json_path):
    """
    Generate JSON using the KDA tool based on the provided YAML template.
    """
    command = f'kda gen -t "{template_path}" -o "{json_path}"'
    returncode, stdout, stderr = await run_command(command)

    if returncode != 0:
        print(f"Error: Failed to generate JSON file.\n{stderr}", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(json_path):
        print(f"Error: JSON file was not created.", file=sys.stderr)
        sys.exit(1)


async def run_kda_local(json_path, network_url):
    """
    Run the 'kda local' command to process the JSON and fetch module data.
    """
    command = f'kda local "{json_path}" -n "{network_url}"'
    returncode, stdout, stderr = await run_command(command)

    if returncode != 0:
        print(f"Error: 'kda local' command failed.\n{stderr}", file=sys.stderr)
        sys.exit(1)

    return stdout


def parse_and_create_files(json_output, network_url):
    """
    Parse the JSON output from 'kda local' and create .pact files accordingly.
    """
    try:
        data = json.loads(json_output)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON output.\n{e}", file=sys.stderr)
        sys.exit(1)

    # Access the top-level URL key
    if network_url not in data:
        print(
            f"Error: Network URL '{network_url}' not found in JSON output.",
            file=sys.stderr,
        )
        sys.exit(1)

    network_data = data[network_url]

    if not isinstance(network_data, list):
        print("Error: Expected a list under the network URL key.", file=sys.stderr)
        sys.exit(1)

    for entry in network_data:
        # Navigate to body.result.data
        try:
            result_data = entry["body"]["result"]["data"]
        except KeyError as e:
            print(
                f"Warning: Missing expected key {e} in JSON entry. Skipping.",
                file=sys.stderr,
            )
            continue

        if not isinstance(result_data, list):
            print("Warning: 'data' field is not a list. Skipping.", file=sys.stderr)
            continue

        for module in result_data:
            name = module.get("name")
            code = module.get("code")

            if not name or not code:
                print(
                    "Warning: Missing 'name' or 'code' in JSON entry. Skipping.",
                    file=sys.stderr,
                )
                continue

            # Extract namespace and module name from the name
            if "." in name:
                namespace, module_name = name.rsplit(".", 1)
            else:
                namespace = name
                module_name = "KDA"  # Default name if not present

            # Create directory for the namespace
            try:
                os.makedirs(namespace, exist_ok=True)
            except Exception as e:
                print(
                    f"Error: Failed to create directory '{namespace}'.\n{e}",
                    file=sys.stderr,
                )
                continue

            # Define the filename based on the module's name
            filename = os.path.join(namespace, f"{module_name}.pact")
            try:
                with open(filename, "w") as f:
                    f.write(code)
                # Uncomment the next line if you want to confirm file creation
                # print(f"Created file: {filename}")
            except Exception as e:
                print(
                    f"Error: Failed to write to file '{filename}'.\n{e}",
                    file=sys.stderr,
                )


async def main():
    args = parse_arguments()

    # Paths
    template_path = os.path.abspath("fetch-modules.ktpl")
    substituted_yaml_path = os.path.join(os.getcwd(), "substituted_config.ktpl")
    json_file = os.path.join(os.getcwd(), "temp_fetch_module_code.json")
    network_url = args.network_url

    # Verify template file exists
    if not os.path.isfile(template_path):
        print(
            f"Error: KDA template file '{template_path}' does not exist.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Read YAML template
    try:
        with open(template_path, "r") as f:
            yaml_template_content = f.read()
    except Exception as e:
        print(f"Error: Failed to read KTPL template file.\n{e}", file=sys.stderr)
        sys.exit(1)

    # Substitute placeholders
    substitutions = {
        "chain": args.chain,
        "namespace": args.namespace,
    }
    substituted_yaml_content = substitute_placeholders(
        yaml_template_content, substitutions
    )

    # Write substituted YAML to a temporary file
    try:
        with open(substituted_yaml_path, "w") as f:
            f.write(substituted_yaml_content)
    except Exception as e:
        print(f"Error: Failed to write substituted YAML file.\n{e}", file=sys.stderr)
        sys.exit(1)

    # Generate JSON file using the substituted YAML
    await generate_json(substituted_yaml_path, json_file)

    # Run 'kda local' command
    local_output = await run_kda_local(json_file, network_url)

    # Parse JSON output and create files
    parse_and_create_files(local_output, network_url)

    # Clean up temporary files
    try:
        os.remove(json_file)
        os.remove(substituted_yaml_path)
        # Uncomment the next lines if you want to confirm deletions
        # print(f"Deleted temporary JSON file: {json_file}")
        # print(f"Deleted substituted YAML file: {substituted_yaml_path}")
    except Exception as e:
        print(f"Warning: Failed to delete temporary files.\n{e}", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
