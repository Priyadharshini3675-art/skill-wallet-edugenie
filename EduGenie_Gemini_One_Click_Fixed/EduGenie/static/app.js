"use strict";
const tools = {
 qa: { title:"Ask EduGenie",desc:"Have a question? Your AI tutor is here to help.",label:"Your question",placeholder:"e.g. Why is the sky blue?",button:"Get answer",badge:"Q&A",response:"Your answer" },
 explain: {title:"Explain a concept",desc:"Make tricky topics easier to understand.",label:"Concept or topic",placeholder:"e.g. How does photosynthesis work?",button:"Explain concept",badge:"EXPLAIN",response:"Simple explanation"},
 quiz: {title:"Quiz generator",desc:"Practice with 3 multiple-choice questions and instant feedback.",label:"Topic or educational passage",placeholder:"e.g. The Pythagorean theorem, or paste a passage",button:"Generate quiz",badge:"QUIZ",response:"Your practice quiz"},
 summarize: {title:"Summarize text",desc:"Turn long passages into simple revision notes.",label:"Paste your passage",placeholder:"Paste your educational text here...",button:"Summarize",badge:"SUMMARY",response:"Your summary"},
 learn: {title:"Learning roadmap",desc:"Create a personalized, week-by-week study plan.",label:"What would you like to learn?",placeholder:"e.g. SQL, Python programming, Algebra",button:"Build study plan",badge:"ROADMAP",response:"Your study plan"}
};
let current="qa", lastOutput="";
const $ = id => document.getElementById(id);
function selectTool(tool){
 if(!tools[tool])return;
 current=tool; const t=tools[tool];
 document.querySelectorAll("[data-tool]").forEach(x=>{x.classList.toggle("active",x.classList.contains("nav")&&x.dataset.tool===tool);x.classList.toggle("selected",x.classList.contains("tile")&&x.dataset.tool===tool)});
 $("breadcrumb").textContent=$("tool-title").textContent=t.title;
 $("tool-description").textContent=t.desc;$("prompt-label").textContent=t.label;$("prompt").placeholder=t.placeholder;
 $("submit-label").textContent=t.button;$("feature-badge").textContent=t.badge;
 $("tool-number").textContent=String(Object.keys(tools).indexOf(tool)+1).padStart(2,"0")+" / STUDY TOOL";
 $("level-settings").hidden=!(tool==="explain"||tool==="learn");$("weeks-settings").hidden=tool!=="learn";
 $("result-section").hidden=true;$("error").hidden=true;$("prompt").value="";
}
document.querySelectorAll("[data-tool]").forEach(b=>b.addEventListener("click",()=>selectTool(b.dataset.tool)));
function makeNode(tag,text,cls){const n=document.createElement(tag); if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n}
function renderQuiz(items){
 const root=$("result");root.replaceChildren();$("quiz-score").hidden=true;
 const answers=new Map();
 items.forEach((q,i)=>{
  const card=makeNode("div",undefined,"quiz-item");card.append(makeNode("h3",`Question ${i+1}. ${q.question}`));
  const feedback=makeNode("div", "", "quiz-feedback");feedback.hidden=true;
  q.options.forEach(option=>{const label=makeNode("label",undefined,"quiz-option");const input=document.createElement("input");input.type="radio";input.name="question_"+i;input.value=option;input.addEventListener("change",()=>{answers.set(i,option);feedback.hidden=true;$("quiz-score").hidden=true});label.append(input,document.createTextNode(option));card.append(label)});
  const check=makeNode("button","Check answer","copy-btn");check.type="button";
  check.addEventListener("click",()=>{const choice=answers.get(i);feedback.hidden=false;if(!choice){feedback.textContent="Select an answer first.";feedback.className="quiz-feedback wrong";return}const correct=choice===q.answer;feedback.className="quiz-feedback"+(correct?"":" wrong");feedback.textContent=(correct?"✓ Correct! ":`✗ Correct answer: ${q.answer}. `)+(q.explanation||"");});
  card.append(check,feedback);root.append(card);
 });
 const finish=makeNode("button","Finish quiz & see score","primary");finish.type="button";finish.style.marginTop="20px";
 finish.addEventListener("click",()=>{const score=items.reduce((s,q,i)=>s+(answers.get(i)===q.answer?1:0),0);$("quiz-score").textContent=`You scored ${score} / ${items.length}. ${answers.size<items.length?"Some questions are unanswered.":"Great work—keep practicing!"}`;$("quiz-score").hidden=false;items.forEach((q,i)=>{const feedback=root.querySelectorAll(".quiz-feedback")[i];feedback.hidden=false;const good=answers.get(i)===q.answer;feedback.className="quiz-feedback"+(good?"":" wrong");feedback.textContent=(good?"✓ Correct. ":`✗ Correct answer: ${q.answer}. `)+(q.explanation||"")})});
 root.append(finish);
 lastOutput=items.map((q,i)=>`${i+1}. ${q.question}\n${q.options.join("\n")}\nAnswer: ${q.answer}\n${q.explanation}`).join("\n\n");
}
$("study-form").addEventListener("submit",async(e)=>{
 e.preventDefault();const text=$("prompt").value.trim();if(text.length<2){$("error").textContent="Please enter at least two characters.";$("error").hidden=false;return}
 const level=$("level").value,weeks=Number($("weeks").value);
 const targets={qa:["/qa?"+new URLSearchParams({question:text}),"GET"],explain:["/explain","POST",{topic:text,level}],quiz:["/quiz","POST",{text}],summarize:["/summarize","POST",{text}],learn:["/learn/recommendations","POST",{topic:text,level,weeks}]};
 const [url,method,body]=targets[current],which=current;$("error").hidden=true;$("result-section").hidden=true;$("submit").disabled=true;$("submit-label").textContent="Thinking…";
 try{
  const res=await fetch(url,{method,headers:{"Content-Type":"application/json"},...(body?{body:JSON.stringify(body)}:{})});
  let data;try{data=await res.json()}catch{throw new Error("The server returned an unreadable response.")}
  if(!res.ok){let detail=data.detail||"The request failed";if(Array.isArray(detail))detail=detail.map(x=>x.msg).join("; ");throw new Error(detail)}
  if(which!==current)return;
  $("result-heading").textContent=tools[which].response;$("result-section").hidden=false;$("quiz-score").hidden=true;
  if(which==="quiz"){if(!Array.isArray(data.quiz))throw new Error("Invalid quiz response.");renderQuiz(data.quiz)}else{lastOutput=data.answer||data.explanation||data.summary||data.recommendation||"No response";$("result").textContent=lastOutput}
  $("result-section").scrollIntoView({behavior:"smooth",block:"start"});
 }catch(err){$("error").textContent=err.message||"Unable to connect. Is the backend running?";$("error").hidden=false}
 finally{$("submit").disabled=false;$("submit-label").textContent=tools[current].button}
});
$("copy").addEventListener("click",async()=>{try{await navigator.clipboard.writeText(lastOutput);$("copy").textContent="Copied!";setTimeout(()=>$("copy").textContent="Copy result",1500)}catch{$("copy").textContent="Copy unavailable"}});
