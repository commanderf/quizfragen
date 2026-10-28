(() => {
  'use strict';
  const Q = window.QUIZ_QUESTIONS || [];
  const categories = ['Musik','Film & Fernsehen','Alltag & Technik','Zeitgeschehen & Sport'];
  const difficulties = ['alle','leicht','mittel','schwer'];
  const decades = ['70er','80er','90er','00er'];
  const $ = s => document.querySelector(s);
  const $$ = s => [...document.querySelectorAll(s)];
  const state = {decade:'70er', categories:[...categories], count:20, difficulty:'alle', round:[], pos:0, score:0, answers:[]};
  const views = {home:$('#homeView'),setup:$('#setupView'),quiz:$('#quizView'),result:$('#resultView')};
  const esc = s => String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
  const shuffle = a => {a=[...a]; for(let i=a.length-1;i;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]} return a};
  const GAME_KEY='zrRunningGame';
  const byId=new Map(Q.map(q=>[q.id,q]));
  function saveGame(){try{if(!state.round.length)return;const g={roundIds:state.round.map(q=>q.id),pos:state.pos,score:state.score,answers:state.answers.map(a=>({id:a.q.id,selected:a.selected}))};localStorage.setItem(GAME_KEY,JSON.stringify(g))}catch{}}
  function loadGame(){try{const g=JSON.parse(localStorage.getItem(GAME_KEY));if(!g||!Array.isArray(g.roundIds)||!Array.isArray(g.answers))return null;const round=g.roundIds.map(id=>byId.get(id)).filter(Boolean);if(round.length!==g.roundIds.length)return null;const answers=g.answers.slice(0,g.pos).map(a=>{const q=byId.get(a.id);if(!q||!q.answers.includes(a.selected))return null;return {q,selected:a.selected,correct:a.selected===q.correct}});if(answers.some(a=>!a))return null;return {...g,round,answers:sliceOk(answers,g.pos)}}catch{return null}}
  function sliceOk(arr,n){const out=[];for(let i=0;i<n&&i<arr.length;i++)out.push(arr[i]);return out}
  function clearGame(){try{localStorage.removeItem(GAME_KEY)}catch{}}
  function refreshResume(){
    const box=$('#resumeBox'); if(!box)return;
    const g=loadGame();
    if(g&&g.pos<g.round.length){box.hidden=false;$('#resumeInfo').textContent=`${g.round.length-g.pos} von ${g.round.length} Fragen offen · ${g.score} richtig`;}
    else box.hidden=true;
  }
  function show(name){Object.values(views).forEach(v=>v.classList.remove('active'));views[name].classList.add('active');if(name==='home')refreshResume();scrollTo({top:0,behavior:'smooth'})}
  function toast(msg){const n=document.createElement('div');n.className='toast';n.textContent=msg;document.body.append(n);setTimeout(()=>n.remove(),2300)}
  function option(name,value,label,checked,type='radio') {return `<div class="choice"><input type="${type}" name="${name}" id="${name}-${encodeURIComponent(value)}" value="${esc(value)}" ${checked?'checked':''}><label for="${name}-${encodeURIComponent(value)}">${esc(label)}</label></div>`}
  function setup(decade='70er', mixed=false){
    if(mixed){
      state.decade='alle';
    }else if(decade==='alle' || decade==='beide'){
      state.decade='alle';
    }else{
      state.decade=decade;
    }
    state.categories=[...categories]; state.count=20; state.difficulty='alle';
    let html = decades.map(d=>option('decade',d,d,state.decade===d)).join('') + option('decade','alle','Alle Jahrzehnte',state.decade==='alle');
    $('#decadeOptions').innerHTML=html;
    $('#categoryOptions').innerHTML=categories.map(c=>option('category',c,c,true,'checkbox')).join('');
    $('#countOptions').innerHTML=[10,20,30,40].map(n=>option('count',n,n+' Fragen',n===20)).join('');
    $('#difficultyOptions').innerHTML=difficulties.map(d=>option('difficulty',d,d[0].toUpperCase()+d.slice(1),d==='alle')).join('');
    $$('#setupView input').forEach(i=>i.addEventListener('change',updateSetup)); updateSetup(); show('setup');
  }
  function updateSetup(){
    state.decade=$('input[name=decade]:checked').value;
    state.categories=$$('input[name=category]:checked').map(x=>x.value);
    state.count=Number($('input[name=count]:checked').value);
    state.difficulty=$('input[name=difficulty]:checked').value;
    const pool=getPool(); $('#availableNote').textContent=`${pool.length} passende Fragen verfügbar`;
    $('#startBtn').disabled=!pool.length||!state.categories.length;
  }
  function getPool(){return Q.filter(q=>(state.decade==='alle'||state.decade==='beide'||q.decade===state.decade)&&state.categories.includes(q.category)&&(state.difficulty==='alle'||q.difficulty===state.difficulty))}
  function start(){
    const pool=getPool(); if(!pool.length)return;
    state.round=shuffle(pool).slice(0,Math.min(state.count,pool.length)); state.pos=0;state.score=0;state.answers=[];saveGame();show('quiz');renderQuestion();
  }
  function renderQuestion(){
    const q=state.round[state.pos]; $('#progressText').textContent=`Frage ${state.pos+1} von ${state.round.length}`;$('#scoreText').textContent=`${state.score} richtig`;$('#progressBar').style.width=`${state.pos/state.round.length*100}%`;
    $('#categoryBadge').textContent=q.category;$('#difficultyBadge').textContent=q.difficulty;$('#questionText').textContent=q.question;$('#feedback').hidden=true;
    $('#answers').innerHTML=shuffle(q.answers).map(a=>`<button class="answer-btn" type="button" data-answer="${esc(a)}">${esc(a)}</button>`).join('');
    $$('.answer-btn').forEach(b=>b.addEventListener('click',()=>answer(b.dataset.answer)));
  }
  function answer(value){
    if(state.answers.length>state.pos)return;
    const q=state.round[state.pos], correct=value===q.correct;if(correct)state.score++;
    state.answers.push({q,selected:value,correct});saveGame();
    $$('.answer-btn').forEach(b=>{b.disabled=true;if(b.dataset.answer===q.correct)b.classList.add('correct');else if(b.dataset.answer===value)b.classList.add('wrong')});
    $('#feedbackTitle').textContent=correct?'Richtig!':'Nicht ganz.';$('#explanation').textContent=q.explanation;$('#sourceLink').href=q.source;$('#feedback').hidden=false;$('#scoreText').textContent=`${state.score} richtig`;
    $('#nextBtn').innerHTML=state.pos===state.round.length-1?'Ergebnis <span>→</span>':'Weiter <span>→</span>';
  }
  function next(){if(state.pos>=state.round.length||state.answers.length<=state.pos)return;if(++state.pos>=state.round.length)finish();else{saveGame();renderQuestion()}}
  function finish(){
    const pct=Math.round(state.score/state.round.length*100);$('#resultPercent').textContent=pct+'%';$('#resultDial').style.setProperty('--p',pct+'%');
    const [title,copy]=pct>=90?['Zeitreise-Profi!','Du kennst die Jahrzehnte bis ins Detail.']:pct>=70?['Stark erinnert!','Da sind erstaunlich viele Erinnerungen hängengeblieben.']:pct>=50?['Solide Zeitreise','Vieles sitzt – und manches wurde gerade wieder aufgefrischt.']:['Noch eine Runde?','Die Zeitmaschine ist warmgelaufen. Beim nächsten Mal geht mehr.'];
    $('#resultTitle').textContent=title;$('#resultCopy').textContent=copy;
    const wrong=state.round.length-state.score;$('#resultStats').innerHTML=`<div class="stat-box"><strong>${state.score}</strong><span>Richtig</span></div><div class="stat-box"><strong>${wrong}</strong><span>Daneben</span></div><div class="stat-box"><strong>${state.round.length}</strong><span>Fragen</span></div>`;
    $('#reviewList').innerHTML=state.answers.map(a=>`<details class="review-item ${a.correct?'ok':'no'}"><summary>${esc(a.q.question)}</summary><p>Deine Antwort: <b>${esc(a.selected)}</b><br>Richtig: <b>${esc(a.q.correct)}</b><br>${esc(a.q.explanation)} · <a href="${esc(a.q.source)}" target="_blank" rel="noopener noreferrer">Quelle</a></p></details>`).join('');
    saveStats(state.score,state.round.length);clearGame();show('result');
  }
  function loadStats(){try{return JSON.parse(localStorage.getItem('zeitreiseStats'))||{rounds:0,questions:0,correct:0}}catch{return{rounds:0,questions:0,correct:0}}}
  function saveStats(correct,total){const s=loadStats();s.rounds++;s.questions+=total;s.correct+=correct;localStorage.setItem('zeitreiseStats',JSON.stringify(s))}
  function showStats(){const s=loadStats(),p=s.questions?Math.round(s.correct/s.questions*100):0;$('#lifetimeStats').innerHTML=`<div class="lifetime-grid"><div class="stat-box"><strong>${s.rounds}</strong><span>Runden</span></div><div class="stat-box"><strong>${s.questions}</strong><span>Fragen</span></div><div class="stat-box"><strong>${s.correct}</strong><span>Richtig</span></div><div class="stat-box"><strong>${p}%</strong><span>Quote</span></div></div>`;$('#statsDialog').showModal()}
  $$('.decade-card').forEach(b=>b.addEventListener('click',()=>setup(b.dataset.decade)));
  if($('#mixedBtn')) $('#mixedBtn').addEventListener('click',()=>setup('70er',true));
  $('#startBtn').addEventListener('click',start);$('#nextBtn').addEventListener('click',next);
  $('#againBtn').addEventListener('click',()=>{
    const d = (state.decade==='alle'||state.decade==='beide') ? '70er' : state.decade;
    setup(d, state.decade==='alle'||state.decade==='beide');
  });
  $$('[data-action=home]').forEach(b=>b.addEventListener('click',()=>show('home')));
  if($('#quitBtn')) $('#quitBtn').addEventListener('click',()=>confirm('Aktuelle Runde wirklich beenden? Du kannst sie später fortsetzen.')&&show('home'));
  $('.brand').addEventListener('click',e=>{e.preventDefault();show('home')});
  if($('#resumeBtn')) $('#resumeBtn').addEventListener('click',()=>{
    const g=loadGame(); if(!g)return;
    state.round=g.round; state.pos=Math.min(g.pos,g.round.length); state.score=g.score; state.answers=g.answers;
    if(state.pos>=state.round.length){finish();return}
    show('quiz');renderQuestion();
  });
  if($('#discardBtn')) $('#discardBtn').addEventListener('click',()=>{clearGame();refreshResume();toast('Gespeicherte Runde verworfen')});
  if($('#statsBtn')) $('#statsBtn').addEventListener('click',showStats);
  if($('.dialog-close')) $('.dialog-close').addEventListener('click',()=>$('#statsDialog').close());
  if($('#resetStats')) $('#resetStats').addEventListener('click',()=>{try{localStorage.removeItem('zeitreiseStats')}catch{}showStats();toast('Statistik zurückgesetzt')});
  if($('#aboutBtn')) $('#aboutBtn').addEventListener('click',()=>toast(`${Q.length} eigenständige Fragen · keine Anmeldung · Daten bleiben im Browser`));
  document.addEventListener('keydown',e=>{if(views.quiz.classList.contains('active')&&!$('#feedback').hidden&&e.key==='Enter')next()});
  // Anzahl der Fragen wird dynamisch angezeigt, kein harter Check mehr
  refreshResume();
})();
