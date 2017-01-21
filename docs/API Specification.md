# Hanabi
### API Specification

Ian Fox

Last updated September 20, 2016

## POST /newgame  
**Query params:** public (boolean) - whether the game is publicly listed on the main page  

### Responses:
* `200 OK`
* `500 Server Error`

## GET /games  
Returns an array of objects:  
```
{
  id: '12345',  
  players: 2
}
```
Games that have been started will not be shown.

## GET /games/:gameid
Returns a game object:  
```
{  
  inPlay: dict,  
  discard: dict,  
  cardsInDeck: integer,  
  turn: integer,  
  hands: array,  
  misfires: integer,  
  hints: integer,
  rainbowIsColour: boolean,
  perfectOrBust: boolean,
  started: boolean  
}
```

### Fields:  
* `inPlay:` dictionary of colour -> array of card objects
* `discard:` dictionary of colour -> array of card objects
* `cardsInDeck:` number of cards remaining in the deck
* `turn:` integer, index of player whose turn it is
* `hands:` array of hand objects  
* `misfires:` integer, 1-3, number of missfires remaining
* `hints:` integer, 0-8, number of hints remaining
* `rainbowIsColour:` boolean, if rainbow counts as its own colour
* `perfectOrBust:` boolean, whether the game is scored partially or not 
* `started:` whether the game is waiting for players or has started

## PUT /games/gameid
Body params (one or more):
* `leave:` string id of the client leaving the game
* `join:` string id of the client joining the game

The following parameters are only open to the group admin:
* `start:` start the game. Game starts if this key is defined
* `rainbowIsColour:` switches the mode of the room
* `perfectOrBust:` switches the mode of the room

All admin requests require a unique `token,` as does leaving a game


### Responses
* `200 OK`
* `500 Something bad happened`

If it was a join request, also returns a unique `token`.


## POST /games/:gameId/action
### Body parameters:  
 * `action_type`: One of hint, discard, play

#### If hint:
 * `player`: index of the player receiving the hint
 * `attribute`: one of colour or number

#### If discard/play
 * `index`: the index within the specified section of the card to discard/play

### Responses
* `200 OK`
* `403 Invalid`: the hint is invalid, it is not the player's turn, etc
