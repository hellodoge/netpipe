## netpipe

API-oriented raw text storage site

### Motivation
- Network remote control using urls
- Painlessly host modifiable static html
- Attach logs to any IOT device and track them anywhere
- Easily send signals from one script to another
- ???

### Features
- No accounts or limitations
- Oversimplified API
- Ability to change your paste or append to it
- Every paste is private

### API reference
Endpoint                 | Method | Description
-------------------------|--------|-------------------------------------
/create                  | GET    | Create new empty paste
/create                  | POST   | Create new paste out of request body
/<public link\>          | GET    | Get raw paste content
/<private link\>         | PUT    | Replace paste with request body
/<private link\>         | PATCH  | Append request body to paste
/<private link\>/<text\> | GET    | Replace paste with \`text\`
