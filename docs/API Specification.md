# Hanabi
### API Specification

Ian Fox

Last updated January 22, 2017

## POST /games/new  
Body params (0 or more):
* `public` (boolean) - whether the game is publicly listed on the main page. Default: `false`
* `rainbowIsColour` (boolean) - whether to treat rainbow as its own colour. Default: `true`
* `hardMode` (boolean) - whether there is only one of each rainbow card. Default: `false`
* `perfectOrBust` (boolean) - whether the game should be scored in binary (you reached 30 or you didn't). Default: `false`
For more information on the latter three options see "Game Options" in the functional spec.

### Responses:
* `201 OK`
* `500 Server Error`

If response was OK, also sends the newly created Game object as a payload, and the following headers:
* `Location`: url to the created game api endpoint  
* `id`: UUID for the admin of the game (the caller of this endpoint)

## GET /games  
Returns an array of pared down game objects:  
```
{
  id: '12345',  
  players: 2,
  perfectOrBust: false,
  rainbowIsColour: false,
  hardMode: false,
  url: 'url to game object api endpoint'
}
```
Games that have been started or are not public will not be shown.

## GET /games/:gameid
Returns a game object:  
```
{  
  url: string,  
  discard: dict,  
  hands: array,  
  hardMode: boolean,  
  deckSize: integer,  
  turn: integer,  
  started: boolean,  
  rainbowIsColour: boolean,  
  perfectOrBust: boolean,  
  inPlay: dict,  
  lastTurn: boolean,  
  lastPlayer: integer or null,  
  misfires: integer,  
  hints: integer
}
```

### Fields:  
* `url:` the url to the api endpoint for the game  
* `discard:` dictionary of integer -> integer (see: card representation)
* `hands:` array of hand objects  
* `hardMode:` whether the game is in hard mode (see: game options)
* `deckSize:` number of cards remaining in the deck  
* `turn:` index of player whose turn it is  
* `started:` whether the game has started  
* `rainbowIsColour:` whether rainbow counts as its own colour (see: game options)  
* `perfectOrBust:` whether the game is in binary scoring mode (see: game options)  
* `inPlay:` dictionary of integer -> integer (see: card representation)  
* `lastTurn:` whether or not it is the last turn (see: game options)
* `lastPlayer:` index of the last player to get a turn if lastTurn is true, null otherwise  
* `misfires:` number of misfires (3 = good, 0 = you're dead)
* `hints:` number of remaining hints (8 = all hints, 0 = no hints)

## PUT /games/:gameid/join
Body params (one or more):

### Responses
* `200 OK`
* `500 Game is full or has started`

If response was OK, returns the following headers:  
* `Location`: url to the joined game api endpoint
* `id`: UUID for the admin of the game (the caller of this endpoint)  

## PUT /games/:gameid/start
Headers:
* `id`: UUID of the user making the request (must match that of the admin of the game)

Starts the game (deals hands, chooses random player to start).

### Responses
* `200 OK`
* `403 Only admin can start the game`
* `500 Cannot start with one player or game in progress`