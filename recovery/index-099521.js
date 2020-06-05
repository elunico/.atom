let canvas;
let bparts = [];
let currentBezier = null;
let beziers = [];



function keyPressed() {
  if (keyCode === ESCAPE) {
    bparts = [];
  }
}



function setup() {

  const xmlButton = select('#to-xml-btn');
  const tagButton = select('#to-tag-btn');
  const p5Button = select('#to-p5-btn');

  xmlButton.mousePressed(() => {

  });

  tagButton.mousePressed(() => {

  });

  p5Button.mousePressed(() => {
    let text = '';
    for (let bezier of beziers) {
      text = `bezier(${bezier.start.x}, ${bezier.start.y}, ${bezier.p1.x}, ${bezier.p1.y}, ${bezier.p2.x}, ${bezier.p2.y}, ${bezier.end.x}, ${bezier.end.y});`
      text += '\n';
    }
    let blob = new Blob([bezier], {
      type: 'text/plain',
      endings: 'native'
    })
  });

  canvas = createCanvas(600, 400);
  let container = select('#canvas-container');
  canvas.parent(container);

  canvas.mouseClicked((event) => {
    let x = event.layerX;
    let y = event.layerY;

    for (let bezier of beziers) {
      let receiver = bezier.receiverFor(x, y);
      if (receiver) {
        receiver.select();
        return;
      }
    }

    bparts.push(new Point(x, y));
    if (bparts.length == 1) {
      bparts[0].endPoint = true;
    } else if (bparts.length == 4) {
      let oldBezzier = currentBezier;
      bparts[3].endPoint = true;
      if (currentBezier) {
        currentBezier.selected = false;
      }
      currentBezier = new Bezier(bparts[0], bparts[1], bparts[2], bparts[3]);
      currentBezier.selected = true;
      beziers.push(currentBezier);
      bparts = [];
    }
  });

}

function mouseDragged() {
  let selectedPoint = beziers.filter((c) => c.hasSelectedPoint()).flatMap(c => c.points()).filter(point => point.selfSelected)[0];
  if (selectedPoint) {
    selectedPoint.x = mouseX;
    selectedPoint.y = mouseY;
  }
}

function draw() {

  background(255);
  for (let bezier of beziers) {
    bezier.show();
  }
  for (let point of bparts) {
    point.show();
  }
}