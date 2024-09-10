package game_server

import (
	"fmt"
)

func main() {
	fmt.Printf("hello!")
	return
}

/*
	TODO:
		- generate golang client for server.proto and import it here
		- set up a test harness
		- set up a fixture for a sample game state
		- implement GetState, returning the fixture
		- wrangle into a test for GetState
		- implement skeleton for ValidateState
		- write tests for invalid states within each board component, like:
			- invalid buildings (off grid, two of one, enclosure over-occupied, etc)
			- invalid partner zoos (two of one)
			- invalid animals (too many for the enclosures we have)
		- implement ValidateState, passing each test

		future directions:
		- spin up game server
			- spin up game server, backed by postgres
			- create database tables
			- backfill with BGA game logs
				- Add a CreateTable rpc
				- In Python, add worker logic to call CreateTable with game logs
			- in stats db, call GetState and render endgame state
		- support play
			- add protos for taking actions
			- add TakeAction rpc and implement it, returning GameState
*/
