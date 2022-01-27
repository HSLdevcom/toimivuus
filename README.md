# Toimivuusseuranta (performance monitoring) POC

This tool aims to produce transit network performance metrics and visualizations based on [HFP data](https://digitransit.fi/en/developers/apis/4-realtime-api/vehicle-positions/).
HSL planners and member municipalities can use them to improve the performance of public transport service.

## Usage

**TODO**.
These instructions wait for the MVP implementation.

### Environment variables

| Variable                               | Description                                                                                                            |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| POSTGRES_{}                            | See [Postgres image](https://registry.hub.docker.com/_/postgres/) readme.                                              |
| HASURA_{}                              | See [Hasura documentation](https://hasura.io/docs/latest/graphql/core/deployment/graphql-engine-flags/reference.html). |
| HFP_STORAGE_CONNECTION_STRING          | Connection string of blob storage account containing raw HFP data files.                                               |
| HFP_STORAGE_CONTAINER_NAME=hfp-v2-test | Name of the blob container where HFP `.zst` files are located.                                                         |

## Development

Start by cloning this repo to your local machine.
To get the services up and running, you will need [docker-compose](https://docs.docker.com/compose/install/) and [Hasura](https://hasura.io/docs/latest/graphql/core/index.html).

Create the `.env` file so `docker-compose.yml` can read environment variables from there:

```
cp .env.example .env
```

Remember to change any configurations and credentials to suit your dev or production needs.
*Currently, only development usage is assumed, without much safety!*

Start the services and apply database migrations:

```
docker-compose up -d      # Leave out -d to see logs interactively on the console
cd database/hasura
hasura migrate apply
hasura metadata apply
```

## Contact

Arttu Kosonen, [@datarttu](https://github.com/datarttu), arttu.kosonen (at) hsl.fi