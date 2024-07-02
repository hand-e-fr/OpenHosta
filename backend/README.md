# backend

## Routes
### [POST] /tic-tac-toe
#### Request
```json
{
    "board": [
        ["-", "-", "-"],
        ["-", "X", "-"],
        ["-", "-", "-"]
    ]
}
```
#### Response
draw:
```json
{
    "board": [
        ["-", "O", "-"],
        ["-", "X", "-"],
        ["-", "-", "-"]
    ],
    "status": "draw"
}
```
win:
```json
{
    "board": [
        ["X", "O", "O"],
        ["X", "X", "O"],
        ["-", "-", "O"]
    ],
    "status": "win"
}
```