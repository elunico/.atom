// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Interactive Selection
// http://www.genarts.com/karl/papers/siggraph91.html

const COLORS = 5;

//Constructor (makes a random DNA)
class DNA {
  constructor(newgenes) {
    // DNA is random floating point values between 0 and 1 (!!)
    // The genetic sequence
    let len = COLORS; // COLORS RGB colors in a scheme
    if (newgenes) {
      this.genes = newgenes;
    } else {
      this.genes = new Array(len);
      for (let i = 0; i < this.genes.length; i++) {
        this.genes[i] = {
          red: random(1),
          blue: random(1),
          green: random(1)
        };
      }
    }
  }

  // Crossover
  // Creates new DNA sequence from two (this &
  crossover(partner) {
    let stops = Array(this.genes.length).fill(1).map((v, i, arr) => i);
    let zeros = Array(this.genes.length / 3).fill(0);
    stops.concat(zeros);

    let child = new Array(this.genes.length);
    let crossover = floor(random(this.genes.length));
    for (let i = 0; i < this.genes.length; i++) {
      if (i > crossover) child[i] = this.genes[i];
      else child[i] = partner.genes[i];
    }
    let newgenes = new DNA(child);
    return newgenes;
  }

  // Based on a mutation probability, picks a new random character in array spots
  mutate(m) {
    for (let i = 0; i < this.genes.length; i++) {
      if (random(1) < m) {
        this.genes[i] = {
          red: random(1),
          blue: random(1),
          green: random(1)
        };
      }
    }
  }
}