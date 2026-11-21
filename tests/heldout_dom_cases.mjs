// Seeded synthetic cases for checking fresh DOM grounding without a live browser.
const applications=['archive','board','calendar','catalog','inbox','workspace'];
const verbs=['Add','Approve','Archive','Move','Open','Publish','Review','Save'];
const objects=['draft','folder','item','note','record','request','report','task'];

function seededRandom(value){
  if(!Number.isInteger(value)||value<0||value>0xffffffff)
    throw new Error('seed must be an unsigned 32-bit integer');
  let state=value||0x9e3779b9;
  return ()=>{
    state^=state<<13;state^=state>>>17;state^=state<<5;
    return (state>>>0)/0x100000000;
  };
}

function shuffled(items,random){
  const result=[...items];
  for(let i=result.length-1;i>0;i--){
    const j=Math.floor(random()*(i+1));
    [result[i],result[j]]=[result[j],result[i]];
  }
  return result;
}

/** Generate cases whose task targets omit all screen coordinates. */
export function generateHeldoutCases(seed=20261121,count=12){
  if(!Number.isInteger(count)||count<1||count>50)
    throw new Error('case count must be 1..50');
  const random=seededRandom(seed);
  const labels=shuffled(verbs.flatMap(verb=>objects.map(object=>`${verb} ${object}`)),random);
  const cells=shuffled(Array.from({length:20},(_,index)=>index),random);
  const cases=[];
  for(let index=0;index<count;index++){
    const caseLabels=shuffled(labels,random).slice(0,5);
    const actionCount=2+Math.floor(random()*2);
    const actionIds=shuffled(caseLabels.slice(0,actionCount).map((_,i)=>`target-${i+1}`),random);
    const controlOrder=shuffled(caseLabels,random);
    const controls=controlOrder.map((name,order)=>{
      const cell=cells[(index*5+order)%cells.length];
      const column=cell%4,row=Math.floor(cell/4);
      return {
        id:`target-${caseLabels.indexOf(name)+1}`,
        name,
        rect:{
          x:column*25+1+Math.floor(random()*3),
          y:row*20+1+Math.floor(random()*4),
          width:10+Math.floor(random()*9),
          height:9+Math.floor(random()*7),
        },
      };
    });
    const app=applications[Math.floor(random()*applications.length)];
    cases.push({
      id:`heldout-${String(index+1).padStart(2,'0')}`,
      application:app,
      controls,
      sequence:actionIds,
      statusText:`Complete ${app} case ${index+1}`,
    });
  }
  return cases;
}
