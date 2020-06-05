let brain;

function setup() {

  createCanvas(200, 200);
  pixelDensity(1);
  brain = new NeuralNetwork(2, 5, 1);
  background(0);
}

function keyPressed() {
  if (key == ' ') {
    noLoop();
  }
}

function draw() {
  for (let i = 0; i < 55; i++) {
    brain.train([0, 0], [0]);
    brain.train([0, 1], [1]);
    brain.train([1, 0], [1]);
    brain.train([1, 1], [0]);
  }

  loadPixels();
  for (let x = 0; x < width; x++) {
    for (let y = 0; y < height; y++) {
      let idx = (x + y * width) * 4;
      let prediction = brain.predict([x / width, y / height])[0];
      pixels[idx] = prediction * 255;
      pixels[idx + 1] = prediction * 255;
      pixels[idx + 2] = prediction * 255;
    }
  }
  updatePixels();
}