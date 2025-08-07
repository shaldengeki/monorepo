package server

import (
	"sync"
	"sync/atomic"

	"github.com/shaldengeki/monorepo/games/tictactoe/proto"
)

type Board struct {
	sync.RWMutex
	board      proto.Board
	totalMoves atomic.Uint64
	nextID     uint32
	seqNum     uint64
}

func NewBoard() *Board {
	return &Board{
		nextID:     1,
		seqNum:     uint64(1),
		totalMoves: atomic.Uint64{},
	}
}
