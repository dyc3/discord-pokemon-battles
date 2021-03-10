# discord-pokemon-battles

SSW 215 Final Project

# Setup

Required:

-   docker
-   docker-compose
    -   https://docs.docker.com/compose/install/

Put your discord bot's token in the `token` file.

# Developing

```
docker-compose up
```

To force a rebuild:

```
docker-compose up --build
```

The battle API is served over port 4000, and the flask server is served over port 5000.

# Commands

Commands are subject to change since we are in the development stage at the moment. This will be an evolving list of commands!

Prefix: `p!`

`ping` will return `pong`

`sim bid` will simulate a pokemon battle, and will return `Simulating battle bid...`
