/* StudySprint validation build: browser-only storage and transparent document heuristics. */
(function(){
  'use strict';
  const KEY='studysprint.validation.v1';
  const defaults={name:'',course:'',papers:[],pyqAnalysis:null,pyqSubject:'',apiBaseUrl:'http://127.0.0.1:8000',examName:'',examDate:'',focusSeconds:0,completedSessions:0,studyDays:[],lastStudyDate:'',tasks:[]};
  let data=loadData(),selectedPyq=[],timerSeconds=25*60,timerRunning=false,timerInterval=null;
  const $=id=>document.getElementById(id);
  function loadData(){try{const saved=JSON.parse(localStorage.getItem(KEY)||'{}');return Object.assign({},defaults,saved,{topics:[]});}catch(e){return {...defaults};}}
  function save(){localStorage.setItem(KEY,JSON.stringify(data));renderAll();}
  function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
  function toast(message){const el=$('toast');el.textContent=message;el.classList.add('show');setTimeout(()=>el.classList.remove('show'),2600);}
  function todayKey(){const d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');}
  function dateLabel(value){if(!value)return '';return new Date(value+'T00:00:00').toLocaleDateString(undefined,{day:'numeric',month:'short',year:'numeric'});}
  const pageMeta={home:['YOUR STUDY SPACE','Good to see you.','A focused workspace for evidence-based exam preparation.'],pyq:['CORE ENGINE','PYQ Intelligence','Extract questions, compare patterns and inspect supporting evidence.'],focus:['EXECUTION','Focus & Deadline','Protect time for deliberate study.'],profile:['SETTINGS','Your profile','A simple, private study space on this device.']};
  function navigate(view){document.querySelectorAll('.view').forEach(v=>v.classList.toggle('active',v.id==='view-'+view));document.querySelectorAll('.nav button').forEach(b=>b.classList.toggle('active',b.dataset.view===view));$('eyebrow').textContent=pageMeta[view][0];$('pageTitle').textContent=pageMeta[view][1];$('pageSub').textContent=pageMeta[view][2];window.scrollTo({top:0,behavior:'smooth'});}
  document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>navigate(b.dataset.view)));
  document.querySelectorAll('[data-go]').forEach(b=>b.addEventListener('click',()=>navigate(b.dataset.go)));
  $('todayDate').textContent=new Date().toLocaleDateString(undefined,{weekday:'short',day:'numeric',month:'short'});
  function renderAll(){renderHome();renderPyq();renderFocus();$('avatar').textContent=(data.name||'S').trim().charAt(0).toUpperCase();$('studentName').value=data.name||'';$('studentCourse').value=data.course||'';$('apiBaseUrl').value=data.apiBaseUrl||defaults.apiBaseUrl;}
  function renderHome(){
    // Overview metrics are based only on uploaded PYQ analysis and focus activity.
    const paperCount=new Set(data.papers.flatMap(p=>p.paperNames||[])).size;
    const questionCount=data.papers.reduce((sum,p)=>sum+(p.count||0),0);
    $('statTopics').textContent=paperCount;
    $('statDone').textContent=data.papers.length;
    $('statFocus').textContent=Math.floor(data.focusSeconds/60)+'m';
    $('missionCount').textContent=data.papers.length+' pattern groups';
    $('homeTasks').innerHTML=data.papers.length
      ? data.papers.slice(0,4).map(p=>'<div class="task"><span class="tag">'+(p.count||0)+'×</span><div style="min-width:0;flex:1"><div class="task-title">'+escapeHtml(p.label||p.topic||'Question pattern')+'</div><div class="task-meta">'+escapeHtml((p.paperNames||[]).join(', '))+'</div></div></div>').join('')
      : '<div class="empty"><b>No PYQ evidence yet</b>Upload previous-year papers to discover recurring question patterns. The report will show the papers behind each finding.</div>';
    $('homeDeadline').innerHTML=data.examDate
      ? '<div class="eyebrow">'+escapeHtml(data.examName||'UPCOMING EXAM')+'</div><div class="streak-number">'+daysUntil(data.examDate)+'</div><div class="muted tiny">days remaining · '+dateLabel(data.examDate)+'</div>'
      : '<div class="empty"><b>No exam date added</b>Add your next exam in Focus & Deadline to keep it in view.</div>';
    const days=data.studyDays.length;
    $('streakCount').textContent=days+' day'+(days===1?'':'s');
    $('streakBar').style.width=Math.min(100,days*10)+'%';
    $('streakHint').textContent=days?'Every session is a step forward.':'Start with one focused session today.';
  }
  function daysUntil(date){const a=new Date();a.setHours(0,0,0,0);return Math.ceil((new Date(date+'T00:00:00')-a)/86400000);}
  function renderPyq(){
    $('pyqSummary').textContent=data.pyqAnalysis?data.pyqAnalysis.topics.length+' AI-classified topics':'No papers analyzed yet';
    if(!data.pyqAnalysis){$('pyqResults').innerHTML='<div class="empty"><b>Your evidence-backed report will appear here</b>Upload previous-year papers and connect the Gemini-powered analysis API.</div>';return;}
    const result=data.pyqAnalysis;
    $('pyqResults').innerHTML='<div class="eyebrow">GEMINI-ASSISTED ANALYSIS · '+escapeHtml(result.model||'model')+'</div><h3 style="font:600 17px Space Grotesk;margin:7px 0 4px">'+escapeHtml(result.subject||'Uploaded paper set')+'</h3><div class="tiny muted">'+result.questions_extracted+' extracted question candidates · '+result.papers_received+' papers · Engine '+escapeHtml(result.engine_version)+'</div>'+
      result.topics.map(topic=>'<div class="result-card"><div class="row" style="justify-content:space-between"><h4>'+escapeHtml(topic.topic)+'</h4><span class="tag">'+topic.question_count+' question(s)</span></div><div class="priority-meta">'+topic.paper_count+' of '+result.papers_received+' papers ('+topic.paper_coverage_percent+'%) · '+escapeHtml((topic.papers||[]).join(', '))+'</div><p class="tiny" style="color:#c2cbe2;line-height:1.7">'+escapeHtml(topic.concept_summary)+'</p><div class="notice">'+escapeHtml(topic.confidence_note)+'</div>'+
      (topic.questions||[]).map(q=>'<div class="task" style="margin-top:8px"><div><div class="task-title">'+escapeHtml(q.paper_name)+' · '+escapeHtml(q.question_type)+' · '+escapeHtml(q.difficulty)+'</div><div class="task-meta">'+escapeHtml(q.question_text)+'</div></div></div>').join('')+'</div>').join('')+
      (result.unclassified_questions||[]).length?'<div class="notice">'+result.unclassified_questions.length+' extracted question(s) were not classified and are excluded from topic frequencies.</div>':''+
      (result.warnings||[]).map(w=>'<div class="notice">Review note: '+escapeHtml(w)+'</div>').join('')+
      '<div class="notice">'+escapeHtml(result.evidence_notice)+'</div>';
  }
  function renderFocus(){
    $('examName').value=data.examName||'';$('examDate').value=data.examDate||'';
    $('examCountdown').innerHTML=data.examDate?'<div class="glass" style="padding:17px;background:rgba(100,230,225,.05)"><div class="eyebrow">'+escapeHtml(data.examName||'EXAM COUNTDOWN')+'</div><div class="streak-number">'+daysUntil(data.examDate)+'</div><div class="tiny muted">days until '+dateLabel(data.examDate)+'</div></div>':'<div class="empty">Add an exam date to start your countdown.</div>';
    $('deadlineList').innerHTML=data.examDate?'<div class="calendar-item"><div><strong>'+escapeHtml(data.examName||'Exam')+'</strong><small>'+dateLabel(data.examDate)+'</small></div><span class="tag">'+daysUntil(data.examDate)+' DAYS</span></div>':'<div class="empty">No deadlines added yet.</div>';
  }
    async function extractFile(file){
    const ext=file.name.split('.').pop().toLowerCase();
    if(ext==='txt'||ext==='md')return await file.text();
    if(ext==='pdf'){
      if(!window.pdfjsLib)throw new Error('PDF reader could not load. Check your internet connection and try again.');
      pdfjsLib.GlobalWorkerOptions.workerSrc='https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
      const buffer=await file.arrayBuffer(),pdf=await pdfjsLib.getDocument({data:buffer}).promise;let text='';
      for(let i=1;i<=pdf.numPages;i++){const page=await pdf.getPage(i),content=await page.getTextContent();text+=content.items.map(x=>x.str).join(' ')+'\n';}
      if(text.trim().length<30)throw new Error('This PDF appears to be scanned or image-only. This version reads selectable PDF text; OCR is not enabled yet.');
      return text;
    }
    throw new Error('Please use a PDF, TXT or MD file.');
  }
  let pyqRaw=[];
  $('choosePyq').addEventListener('click',()=>$('pyqFiles').click());
  $('pyqFiles').addEventListener('change',e=>{selectedPyq=Array.from(e.target.files);$('pyqFileList').textContent=selectedPyq.length?selectedPyq.map(f=>f.name).join(' · '):'No papers selected.';});
  $('pyqDrop').addEventListener('dragover',e=>{e.preventDefault();$('pyqDrop').classList.add('drag');});
  $('pyqDrop').addEventListener('dragleave',()=>$('pyqDrop').classList.remove('drag'));
  $('pyqDrop').addEventListener('drop',e=>{e.preventDefault();$('pyqDrop').classList.remove('drag');selectedPyq=Array.from(e.dataTransfer.files);$('pyqFileList').textContent=selectedPyq.map(f=>f.name).join(' · ')||'No papers selected.';});
  $('apiBaseUrl').addEventListener('change',()=>{data.apiBaseUrl=$('apiBaseUrl').value.trim().replace(/\/+$/,'')||defaults.apiBaseUrl;save();});
  $('analyzePyq').addEventListener('click',async()=>{
    if(!selectedPyq.length){toast('Choose one or more papers first.');return;}
    const button=$('analyzePyq');button.disabled=true;button.textContent='Extracting and reasoning…';
    try{
      // Extract selectable text in the browser; only the text and file name are sent to the API.
      const docs=[];for(const file of selectedPyq){docs.push({name:file.name,text:await extractFile(file)});}
      const apiBase=($('apiBaseUrl').value.trim()||defaults.apiBaseUrl).replace(/\/+$/,'');
      data.apiBaseUrl=apiBase;
      const response=await fetch(apiBase+'/api/v1/pyq/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({subject:$('pyqSubject').value.trim(),papers:docs})});
      const result=await response.json();
      if(!response.ok)throw new Error(result.detail||'The PYQ API request failed.');
      data.pyqAnalysis=result;
      data.papers=(result.topics||[]).map(topic=>({label:topic.topic,count:topic.question_count,paperCount:topic.paper_count,paperNames:topic.papers,conceptSummary:topic.concept_summary,confidence:'Gemini classification',examples:(topic.questions||[]).map(q=>({paper:q.paper_name,question:q.question_text}))}));
      data.pyqSubject=$('pyqSubject').value;data.paperNames=docs.map(d=>d.name);save();
      toast('Gemini analyzed '+result.questions_extracted+' extracted question candidates.');
    }catch(err){toast(err.message||'Could not analyze papers. Check your API URL and backend.');}
    finally{button.disabled=false;button.textContent='Analyze papers ↗';}
  });
  // Clearly labelled synthetic examples help test the interface; they are not real exam evidence.
  $('saveExam').addEventListener('click',()=>{if(!$('examDate').value){toast('Choose an exam date.');return;}data.examName=$('examName').value.trim()||'Upcoming exam';data.examDate=$('examDate').value;save();toast('Exam countdown saved.');});
  $('timerStart').addEventListener('click',()=>{if(timerRunning){clearInterval(timerInterval);timerRunning=false;$('timerStart').textContent='Resume';$('timerLabel').textContent='PAUSED';return;}timerRunning=true;$('timerStart').textContent='Pause';$('timerLabel').textContent='FOCUS IN PROGRESS';timerInterval=setInterval(()=>{timerSeconds--;updateTimer();if(timerSeconds<=0){clearInterval(timerInterval);timerRunning=false;data.focusSeconds+=25*60;data.completedSessions++;const day=todayKey();if(!data.studyDays.includes(day))data.studyDays.push(day);save();timerSeconds=25*60;updateTimer();$('timerStart').textContent='Start focus';$('timerLabel').textContent='SESSION COMPLETE · WELL DONE';toast('Focus session completed. Great work!');}},1000);});
  $('timerReset').addEventListener('click',()=>{clearInterval(timerInterval);timerRunning=false;timerSeconds=25*60;updateTimer();$('timerStart').textContent='Start focus';$('timerLabel').textContent='READY WHEN YOU ARE';});
  function updateTimer(){const m=Math.floor(timerSeconds/60),s=timerSeconds%60;$('timerTime').textContent=String(m).padStart(2,'0')+':'+String(s).padStart(2,'0');const progress=(25*60-timerSeconds)/(25*60)*360;$('timerRing').style.background='conic-gradient(var(--cyan) '+progress+'deg,rgba(255,255,255,.07) '+progress+'deg)';}
  $('saveProfile').addEventListener('click',()=>{data.name=$('studentName').value.trim();data.course=$('studentCourse').value.trim();save();toast('Profile saved on this device.');});
  $('exportData').addEventListener('click',()=>{const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='studysprint-my-data.json';a.click();URL.revokeObjectURL(url);});
  $('resetData').addEventListener('click',()=>{if(!confirm('Delete all StudySprint data saved in this browser? This cannot be undone.'))return;localStorage.removeItem(KEY);data={...defaults};save();toast('Local StudySprint data reset.');});
  renderAll();updateTimer();
})();
