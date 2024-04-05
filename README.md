# Python Strategy Executor
A simple trading strategy executor framework to run trading strategies written in Python.

# Starting the Strategy Executor

The easiest way to spin up the strategy executor is to use the make file:

```
make start
```

This is going to spin up all the necessary services. The backend serving the bot-api and the strategy executor running
the strategy.

But before doing this: please make sure to update the `.env` file.

It should contain the following configuration settings:

```
CORE_MAESTRO_API_KEY=xxx
MAESTRO_API_KEY=yyy
SERVER_API_KEY=zzz
SEED_PHRASE=[road, road, road, road, road, anger, anger, anger, anger, anger, antenna, antenna, antenna, antenna, token, token, token, cart, cart, cart, cart, cart, cart, cart]
```

- The `CORE_MAESTRO_API_KEY` and the `MAESTRO_API_KEY` are the maestro keys used for different purposes. For details see the dex-contracts-api documentation.
- `SERVER_API_KEY`: is used to define an api-key that restricts access to the bot api backend. This must be passed with each request.
- `SEED_PHRASE` contains a YAML array with the words of the recovery phrase which is used to derive the wallet managed by the backend.

# Example strategies
Some example strategies are available in the strategies folder. These can be started by using make.

```
 > make start-a # starts strategy
 > make stop # stops the executor

For details please see the Makefile.

# Starting example strategies

To start the example strategy a, you can use make:

``` bash
> make start-a
```

To start the example strategy b, you can use make, but please make sure to stop the previously running strategy first,
so there won't be any issues around the used ports:

``` bash
> make stop
> make start-b
```

# Developing strategies

After spinning up a strategy; one might want to change something in the source code.

This can be easily done in the python code and the changes can be deployed by simply calling `make start` again. This is going to deploy the strategy changes, but won't restart the server, so the changes of the strategy logic could be quickly tested.