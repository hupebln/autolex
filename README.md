# Autolex

Autolex is a project designed to synchronize companies from Lexware Office to Autotask. This tool ensures that your company data is consistently updated across both platforms, improving efficiency and reducing manual data entry.

## Features

- Synchronize company data from Lexware Office to Autotask
- Automated updates to ensure data consistency
- Easy setup and configuration

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/hupebln/autolex.git
    ```
2. Navigate to the project directory:
    ```sh
    cd autolex
    ```
3. Install the required dependencies:
    ```sh
    poetry install
    ```

## Usage
### Manually synchonize

1. Configure your Lexware Office and Autotask credentials via environment variables.
2. Run the synchronization script:
    ```sh
    poetry run autolex sync
    ```

### Webhook

1. Configure your Lexware Office and Autotask credentials via environment variables.
2. Run the server:
    ```sh
    poetry run uwsgi --yaml uwsgi.yaml
    ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or support, please open an issue on the GitHub repository.
