# Hanabi
### API Specification

Ian Fox

Last updated January 22, 2017

## Card Representation
Cards are represented as integers when in the deck, discard, or play. If c is a card then:
* `c mod 10` corresponds to the rank of the card
* `floor(c/10)` corresponds to the colour of the card, as follows:  
    + 0: blue  
    + 1: green  
    + 2: red  
    + 3: white  
    + 4: yellow  
    + 5: rainbow  

## Player Ordering
You are always the player at index 0. Turns go in ascending order.

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
Headers:
* `id`: UUID of the user making the request

Route params:
* `:gameid`: the ID of the game

### Responses
* `200 OK`
* `403 Forbidden` if the id header is missing or not in the game

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
* `hands:` array of arrays of cards (see: player ordering)  
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
Route params:
* `:gameid`: the ID of the game

### Responses
* `200 OK`
* `500 Game is full or has started`

If response was OK, returns the following headers:  
* `Location`: url to the joined game api endpoint
* `id`: UUID for the admin of the game (the caller of this endpoint)  

## PUT /games/:gameid/start
Headers:
* `id`: UUID of the user making the request (must match that of the admin of the game)

Route params:
* `:gameid`: the ID of the game

Starts the game (deals hands, chooses random player to start).

### Responses
* `200 OK`
* `403 Only admin can start the game`
* `500 Cannot start with one player or game in progress`

## PUT /games/:gameid/action
Headers:
* `id`: UUID of the user making the request (must match player whose turn it is)

Route params:
* `:gameid`: the ID of the game

Body Params (all requests):
* `type` (integer) - 0 for hint, 1 for play, 2 for discard  

Body Params (hints):
* `playerIndex` (integer) - index of the player you want to hint
* `colour` (integer) - the colour you want to hint about
* `rank` (integer) - the rank you want to hint about
`colour` and `rank` are mutually exclusive

Body Params (discard or play):
* `cardIndex` (integer) - index of the card you want to discard or play

### Responses
* `200 OK`
* `500 Invalid move`

A move may be invalid if:
* It is not your turn  
* A hint does not match any cards in the players hand  
* You try to hint yourself
* Both colour and rank are specified for hints  
* You try to hint about rainbow when rainbow is not treated as a colour  
* You try to hint when there are no hint tokens  
* You try to discard when there are 8 hint tokens  
