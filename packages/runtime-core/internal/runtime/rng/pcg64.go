package rng

// PCG64 is a permuted congruential generator (64-bit output).
// Reference: O'Neill, PCG: A Family of Simple Fast Space-Efficient Statistically Good Algorithms for Random Number Generation.
type PCG64 struct {
	state uint64
	inc   uint64
}

func newPCG64(initState, initSeq uint64) *PCG64 {
	if initSeq == 0 {
		initSeq = 1
	}
	p := &PCG64{inc: (initSeq << 1) | 1}
	p.state = 0
	p.NextUint64()
	p.state += initState
	p.NextUint64()
	return p
}

func (p *PCG64) NextUint64() uint64 {
	oldState := p.state
	p.state = oldState*6364136223846793005 + p.inc
	xorshifted := uint32(((oldState >> 18) ^ oldState) >> 27)
	rot := oldState >> 59
	return (uint64(xorshifted) >> rot) | (uint64(xorshifted) << ((-int(rot)) & 31))
}
