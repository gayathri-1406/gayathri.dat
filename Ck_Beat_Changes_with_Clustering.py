
from herewego import scrap
import pandas as pd
from sklearn.cluster import DBSCAN
import numpy as np
df=pd.read_csv(r"E:\Gayathri\Cakin Kare\Ck_Beat\New_Source\Workout_Data\OutletsAndDist_Data.csv")

from GeoDistanceLinear import geo_dist

df['Beat']=''
df['Visit Order']=''
df['Travel Distance']=''
df['Travel Time']=''
df['Total Time With Spend']=''
li=[]
main_DF=[]

Fin_main=[]
for i in df.groupby('Note'):
    # if i[0]=='M':
    df1=i[1]
    sales_center=list(df1[['Distributor Latitude','Distibutor Longitude']].values[0])
    li.append(sales_center)
    vo,bt=1,1
    df2=df1
    st=sales_center
    chk=0
    df2['Dist']=df2[['Latitude','Longitude']].apply(lambda w:geo_dist(st,[w[0],w[1]]),axis=1)
    df2=df2[df2['Dist']<=120]
    while 1:
        if len(df2)>0:
            df2['Dist']=df2[['Latitude','Longitude']].apply(lambda w:geo_dist(st,[w[0],w[1]]),axis=1)
            df2.sort_values(by='Dist',inplace=True)

            df3=df2.head(3)
            df3[['Distance', 'Duration']] = df3[['Latitude','Longitude']].apply(lambda w: pd.Series(scrap(st,[w[0],w[1]])), axis=1)
            df3.sort_values(by='Distance',inplace=True)

            chk=(chk+df3.values[0][-1])+10
            tmp=[]
            if chk<=420:
                now=list(df3[['Latitude','Longitude']].values[0])

                tmp.append(df3.head(1))
                
                df2=df2[df2['Unique_Id']!=df3.values[0][0]]
                
                df2['Dist2']=df2[['Latitude','Longitude']].apply(lambda w:geo_dist(now,[w[0],w[1]]),axis=1)

                df4=df2[df2['Dist2']<=0.200]

                df4.rename(columns = {'Dist2':'Distance'}, inplace = True) 
                tmp.append(df4)
                chk=chk+df4['Distance'].sum()+len(df4)*10+len(df4)*1
                df4['Duration']=1
                df2=df2[~df2['Unique_Id'].isin(df4['Unique_Id'].tolist())]
                temp_df=pd.concat(tmp)
                st=temp_df[['Latitude','Longitude']].mean().tolist()

                temp_df['Beat']='Beat'+str(bt)
                temp_df['Total Time With Spend']=chk
                main_DF.append(temp_df)
            else:
                db_beat=pd.concat(main_DF)
                
                area=db_beat['Distance'].mean()
                
                deg_base=0.00001
                
                eps1=format(deg_base*area, ".20f")

                clustering = DBSCAN(eps=0.004, min_samples=4).fit(np.array(db_beat[['Latitude','Longitude']]))
                # clustering.labels_
                db_beat['Cluster Label']=clustering.labels_
                
                Fin_main.append(db_beat)

                print(i[0],'Beat'+str(bt))
                st=sales_center
                chk=0
                bt=bt+1
                vo=1
                main_DF=[]

        else:
            break

pd.concat(Fin_main).to_csv(r'E:\Gayathri\Cakin Kare\Ck_Beat\Output_Samp\All_Beats_With_Clustering.csv')