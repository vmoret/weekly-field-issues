# vimo76/weekly-field-issues

Docker image to retrieve the iTrack field issues and generate a report in `/data` volume mount.

## Usage

Create a `docker-compose.yml` file

```yaml
version: '3'
services:
    notebook:
        image: "vimo76/weekly-field-issues"
        volumes:
        - D:\Data:/data
        environment:
            USER: user
            PASSWORD: password
```

and run it with `docker-compose`.

```bash
docker-compose up
```