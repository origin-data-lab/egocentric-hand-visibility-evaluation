"""Run three MediaPipe Hands passes (full, mirrored, lite) on frames [start, stop) of a video.
Usage: python detect_hands.py <recording_id> <video.mp4> <width> <height> <start> <stop>
Output: $ODL_RAW_DIR/raw_<recording>_<start>.json (default ./raw). Requires mediapipe==0.10.14 (Python <= 3.11)."""
import sys,os,subprocess,json,numpy as np,cv2
os.environ['GLOG_minloglevel']='3'
import mediapipe as mp
H=mp.solutions.hands
rec,path,W,Hh,start,stop=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]),int(sys.argv[6])
p=subprocess.Popen(['ffmpeg','-v','error','-i',path,'-vf',f"select=between(n\\,{start}\\,{stop-1}),scale={W}:{Hh}",'-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE)
full=H.Hands(static_image_mode=True,max_num_hands=2,model_complexity=1,min_detection_confidence=0.5)
lite=H.Hands(static_image_mode=True,max_num_hands=2,model_complexity=0,min_detection_confidence=0.5)
def run(model,img,flipped=False):
    r=model.process(img);out=[]
    for hd,lm in zip(r.multi_handedness or [],r.multi_hand_landmarks or []):
        lab=hd.classification[0].label;sc=hd.classification[0].score
        pts=np.array([[l.x,l.y] for l in lm.landmark])
        if flipped:pts[:,0]=1-pts[:,0];lab={'Left':'Right','Right':'Left'}[lab]
        side={'Right':'L','Left':'R'}[lab]   # MediaPipe assumes mirrored input -> wearer side is opposite of label
        out.append(dict(side=side,score=sc,x0=pts[:,0].min(),x1=pts[:,0].max(),y0=pts[:,1].min(),y1=pts[:,1].max(),wx=pts[0,0],wy=pts[0,1],cx=pts[:,0].mean(),cy=pts[:,1].mean()))
    return out
rows=[];i=start
while True:
    b=p.stdout.read(W*Hh*3)
    if len(b)<W*Hh*3:break
    img=np.frombuffer(b,np.uint8).reshape(Hh,W,3)
    a=run(full,img);fl=run(full,np.ascontiguousarray(img[:,::-1]),True);li=run(lite,img)
    rows.append(dict(frame=i,full=a,flip=fl,lite=li));i+=1
json.dump(rows,open(os.path.join(os.environ.get('ODL_RAW_DIR','raw'),f'raw_{rec}_{start:05d}.json'),'w'),default=float)
print(rec,start,len(rows))
