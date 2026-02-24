# Graphical editors for ExtremeXP   

Holds the graphical editors of the ExtremeXP framework, for designing workflows and experiments. 
It is based on the initial version of the ExtremeXP portal.

1. Run ``docker compose up -d`` on the portal project to create the docker network `extremexp_network` to connect to.
1. Copy (or rename) the ".env.example" file into a file called ".env"
    1. Configure .env
1. In the root folder (i.e. the folder contains `docker-compose.yaml` file) issue:
    ```shell
    sudo docker compose build # only if you need to rebuild before running
    sudo docker compose up -d
    ```
1. Access the app via http://localhost:8001/

### Deploy on SSH

To deploy the framework on a server with public IP, you need to change the `VITE_API_URL` for the frontend HTTP request in `web-app/.env`.
For example,

```javascript
// for local development
VITE_API_URL = 'http://127.0.0.1/';

// for SSH deployment
VITE_API_URL = 'http://145.1xx.2xx.2x/';
