const {
  Engine,
  World,
  Body,
  Bodies,
  Vector
} = Matter;

class Rectangle {
  constructor(x, y, w, h, fixed) {
    this.w = w;
    this.h = h;
    this.fixed = fixed;
    this.body = Bodies.rectangle(x, y, w, h, {
      restitution: 0.0,
      friction: 0.4
    });
    this.color = [255, 255, 255];
    Body.setStatic(this.body, fixed);
    World.add(world, this.body);
  }

  show() {
    noStroke();
    fill(...this.color);
    rectMode(CENTER);
    rect(this.body.position.x, this.body.position.y, this.w, this.h);
  }
}

let world, engine;
let r, floor;
let canvas;

function setup() {
  canvas = createCanvas(600, 400);
  engine = Engine.create();
  world = engine.world;
  r = new Rectangle(200, 200, 30, 30);
  floor = new Rectangle(width / 2, height + height / 2 - 10, width, height, true);
  floor.color = [121, 121, 121];
}

function draw() {
  background(51);
  if (mouseIsPressed)
    Body.applyForce(r.body, Vector.create(mouseX, mouseY), Vector.create(0.0002, 0))

  Engine.update(engine);
  r.show();
  floor.show();
}