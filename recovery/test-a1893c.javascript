function verse(voc) {
  const line = Array(3).fill(voc + ' doo'.repeat(6).join('\n'));
  // console.log(line);
  line.forEach(console.log)
  console.log(`${voc}!`);
}

verse('Baby Shark');
verse('Mommy Shark');
verse('Daddy Shark');
verse('Grandma Shark');
verse('Grandpa Shark');
verse("Let's go hunt");
console.log('Run away...');
