/* Raster key poses share the existing rig; speech is a separate face layer. */
const neutralPose=document.getElementById('neutralPose');
const roundMouth=document.getElementById('charMouthRound');
const gestureLayers={};
const motionPreview=new URLSearchParams(location.search).has('motion');
const cuePreview=new URLSearchParams(location.search).has('preview-point');
const onlyOnRequest=new URLSearchParams(location.search).get('gestures')==='hover';
document.documentElement.classList.toggle('mobile-cue-button',
  new URLSearchParams(location.search).get('mobile-dialogue')==='button');
let gesture='neutral', gestureUntil=0, gestureSerial=0, idleIndex=0;
let nextGestureAt=performance.now()+14000, workPromptAt=0, workPromptDone=false;
let lastProjectKey='', lastProjectAt=0, mouthFrameAt=0, mouthShape='closed';

for(const name of ['nails','yawn','thumbs','point']){
  const layer=document.createElement('div');
  layer.className='gesture-pose'; layer.dataset.pose=name;
  layer.setAttribute('aria-hidden','true');
  const makeImage=(file,cls)=>{
    const image=document.createElement('img');
    image.src=`assets/${file}.png`; image.alt=''; image.className=cls;
    layer.appendChild(image); return image;
  };
  const base=makeImage(name==='point'?'gesture-point-up':`gesture-${name}`,'gesture-base');
  let open=null,round=null;
  if(name!=='yawn'){
    open=makeImage(name==='nails'?'nails-open':'02-retro-toon-speaking','mouth-shape');
    round=makeImage(name==='nails'?'nails-round':'mouth-round','mouth-shape');
  }
  charMotion.appendChild(layer);
  const ready=Promise.all([...layer.querySelectorAll('img')].map(img=>img.decode()))
    .then(()=>true,()=>false);
  gestureLayers[name]={layer,base,open,round,ready};
}
const neutralMouthReady=Promise.all([charMouth.decode(),roundMouth.decode()])
  .then(()=>true,()=>false);
let speechImagesReady=false;
neutralMouthReady.then(ready=>{speechImagesReady=ready;});

function resetGesture(){
  gestureSerial++;
  gesture='neutral'; gestureUntil=0;
  neutralPose.style.opacity='1';
  Object.values(gestureLayers).forEach(({layer})=>layer.classList.remove('is-active'));
  charMotion.dataset.pose='neutral';
}
async function playGesture(name,duration=5000){
  if(RM||document.hidden||cvOpen||caseOpen) return;
  const serial=++gestureSerial, pose=gestureLayers[name];
  if(!pose||!await pose.ready||serial!==gestureSerial) return;
  if(document.hidden||cvOpen||caseOpen) return;
  if(name==='yawn'&&typing) return;
  Object.values(gestureLayers).forEach(({layer})=>layer.classList.remove('is-active'));
  neutralPose.style.opacity='0';
  pose.layer.classList.add('is-active');
  gesture=name; gestureUntil=performance.now()+duration;
  charMotion.dataset.pose=name;
  nextGestureAt=gestureUntil+24000+Math.random()*12000;
}
function visibleProject(){
  const entries=[...document.querySelectorAll('.entry[data-key],.tile[data-key]')];
  return entries.filter(el=>{
    const r=el.getBoundingClientRect();
    return r.width>0&&r.top<innerHeight*.78&&r.bottom>100&&
      r.left<innerWidth*.7&&r.right>0;
  }).sort((a,b)=>Math.abs(a.getBoundingClientRect().top-innerHeight*.4)-
    Math.abs(b.getBoundingClientRect().top-innerHeight*.4))[0];
}
function pointToProject(key,force=false){
  if(cvOpen||caseOpen) return;
  const project=PROJECTS.find(p=>p.key===key);
  if(!project) return;
  const now=performance.now();
  if(!force&&key===lastProjectKey&&now-lastProjectAt<9000) return;
  lastProjectKey=key; lastProjectAt=now; workPromptDone=true;
  const line=L==='tr'?`${project.mark} projesini gördün mü?`:
    `Have you seen ${project.mark}?`;
  say(t().proj[key]?.i||'grid',line);
  sayEl.classList.add('project-cue');
  playGesture('point',(motionPreview||cuePreview)?60000:7500);
  renderChips([{
    label:L==='tr'?`${project.mark} projesine bak`:`View ${project.mark}`,
    on:()=>{
      resetGesture();
      const link=document.querySelector(`.entry[data-key="${key}"],.tile[data-key="${key}"]`);
      link?.click();
    }
  }]);
}
function updateCharacterMotion(now){
  if(document.hidden||cvOpen||caseOpen){
    if(gesture!=='neutral')resetGesture();
    return;
  }
  if(gesture!=='neutral'&&(now>gestureUntil||(gesture==='yawn'&&typing)))resetGesture();
  if(gesture==='point'&&zone==='hero')resetGesture();
  // One contextual invitation per visit to Work. Hover/focus remains responsive.
  if(zone==='work'){
    if(!workPromptAt)workPromptAt=now+(cuePreview?500:6500);
    if(!onlyOnRequest&&!workPromptDone&&!typing&&now>workPromptAt){
      const project=visibleProject();
      if(project)pointToProject(project.dataset.key);
    }
  }else{workPromptAt=0;workPromptDone=false;}
  if(!RM&&!motionPreview&&!cuePreview&&!onlyOnRequest&&gesture==='neutral'&&!typing&&now>nextGestureAt){
    playGesture(['nails','thumbs','yawn'][idleIndex++%3],5200);
    nextGestureAt=now+35000;
  }
  const angle=RM?0:Math.sin(now/2900)*1.4+(typing?Math.sin(now/310)*.65:0);
  charHead.style.transform=`rotate(${angle.toFixed(3)}deg)`;
  if(gesture!=='neutral'){
    const sway=Math.sin(now/1100)*.35;
    gestureLayers[gesture].layer.style.transform=`rotate(${sway.toFixed(3)}deg)`;
  }
  // Text-paced visemes: closed consonants, wide vowels and rounded O/U.
  // This is illustrative dialogue animation, not audio phoneme lip-sync.
  if(!typing||RM||!speechImagesReady){mouthShape='closed';}
  else if(now>=mouthFrameAt){
    const letter=txtEl.textContent.trimEnd().slice(-1).toLocaleLowerCase();
    if(/[,.!?;:mbp]/.test(letter)||now%1100>950)mouthShape='closed';
    else if(/[oöuüw]/.test(letter))mouthShape='round';
    else mouthShape=Math.sin(now/100)>.05?'open':'closed';
    mouthFrameAt=now+85;
  }
  charMouth.style.opacity=mouthShape==='open'?'1':'0';
  roundMouth.style.opacity=mouthShape==='round'?'1':'0';
  for(const [name,pose] of Object.entries(gestureLayers)){
    if(pose.open)pose.open.style.opacity=name===gesture&&mouthShape==='open'?'1':'0';
    if(pose.round)pose.round.style.opacity=name===gesture&&mouthShape==='round'?'1':'0';
  }
  charMotion.dataset.mouth=mouthShape;
}
document.addEventListener('visibilitychange',()=>{
  resetGesture(); nextGestureAt=performance.now()+14000;
});
document.addEventListener('focusin',event=>{
  const project=event.target.closest('.entry[data-key],.tile[data-key]');
  if(project)pointToProject(project.dataset.key);
});
if(cuePreview)addEventListener('load',()=>{
  document.getElementById('work').scrollIntoView({behavior:'instant'});
},{once:true});
if(motionPreview){
  const controls=document.createElement('div');
  controls.id='motionControls';controls.className='chips';
  controls.setAttribute('role','group');controls.setAttribute('aria-label','Character motion preview');
  const add=(label,action)=>{
    const button=document.createElement('button');
    button.className='chip';button.textContent=label;button.onclick=action;
    controls.appendChild(button);return button;
  };
  for(const [name,label] of [['nails','Nails'],['yawn','Yawn'],['thumbs','Thumbs up']]){
    add(label,()=>{
      clearTimeout(typeTimer);typing=false;txtEl.setAttribute('aria-busy','false');
      playGesture(name,60000);
    });
  }
  add('Point to a project',()=>{
    const visible=visibleProject();
    if(visible){pointToProject(visible.dataset.key,true);return;}
    scrollToSection('work');
    setTimeout(()=>{const project=visibleProject();if(project)pointToProject(project.dataset.key,true);},1100);
  });
  add('Speak',()=>{
    say('spark',"You can explore my work while I show you what I have been building.");
    if(gesture!=='neutral')gestureUntil=performance.now()+60000;
  });
  add('Reset',()=>{resetGesture();nextGestureAt=performance.now()+24000;});
  document.body.appendChild(controls);
}
