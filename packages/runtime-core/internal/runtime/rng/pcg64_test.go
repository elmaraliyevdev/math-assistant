package rng

import "testing"

func TestPCG64Deterministic(t *testing.T) {
	a := newPCG64(12345, 54)
	b := newPCG64(12345, 54)
	for i := 0; i < 20; i++ {
		if a.NextUint64() != b.NextUint64() {
			t.Fatalf("diverged at draw %d", i)
		}
	}
}

func TestPCG64DifferentSeeds(t *testing.T) {
	a := newPCG64(1, 54)
	b := newPCG64(2, 54)
	if a.NextUint64() == b.NextUint64() {
		t.Fatal("different seeds should produce different first draw")
	}
}

func TestPCG64ZeroSeqCoerced(t *testing.T) {
	p := newPCG64(99, 0)
	if p.inc == 0 {
		t.Fatal("zero initSeq must be coerced to non-zero inc")
	}
	if p.NextUint64() == 0 && p.NextUint64() == 0 {
		// extremely unlikely; still exercises stream
		t.Fatal("PCG64 produced only zeros")
	}
}
