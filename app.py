import streamlit as st
import numpy as np


st.set_page_config(page_title="IceForm", layout="wide")

# ===================== PREMIUM UI =====================

st.markdown("""
<style>

[data-testid="stAppViewContainer"]{
background:linear-gradient(135deg,#eef2f7,#dde6f1,#e9eef5);
}

.main-title{
font-size:36px;
font-weight:800;
color:#0B3C5D;
}

.sub-title{
font-size:14px;
color:#6b7280;
margin-bottom:15px;
}

.card{
padding:22px;
border-radius:14px;
background:white;
box-shadow:0px 8px 25px rgba(0,0,0,0.06);
margin-bottom:22px;
}

.section-title{
font-size:18px;
font-weight:600;
margin-bottom:12px;
}

.kpi-card{
background:linear-gradient(135deg,#0B3C5D,#145DA0);
padding:35px;
border-radius:16px;
color:white;
text-align:center;
box-shadow:0px 10px 30px rgba(11,60,93,0.25);
}

.kpi-number{
font-size:46px;
font-weight:800;
}

.kpi-label{
font-size:14px;
}

.breakdown-grid{
display:grid;
grid-template-columns:1fr 1fr;
gap:10px 30px;
margin-top:15px;
}

.breakdown-item{
font-size:15px;
padding:6px 0;
}

</style>
""",unsafe_allow_html=True)

st.markdown('<div class="main-title">IceForm</div>',unsafe_allow_html=True)
st.markdown('<div class="sub-title">Scientific Ice Cream Formulation Engine</div>',unsafe_allow_html=True)

st.divider()



# ===================== INPUT =====================



st.markdown('<div class="card">',unsafe_allow_html=True)
st.markdown('<div class="section-title">Target</div>',unsafe_allow_html=True)

T=st.number_input("Total Mix (kg)",min_value=0.0)

fat_target=st.number_input("Target Fat (%)")
snf_target=st.number_input("Target SNF (%)")
sugar_target=st.number_input("Target Sugar (%)")

st.markdown('</div>',unsafe_allow_html=True)

# ===================== INGREDIENT SELECTION =====================

st.markdown('<div class="card">',unsafe_allow_html=True)
st.markdown('<div class="section-title">Select Dairy Ingredients (Max 3)</div>',unsafe_allow_html=True)

dairy_options=["Milk","Cream","AMF","White Butter","SMP","WMP","SCM"]

ing1=st.selectbox("Ingredient 1",["None"]+dairy_options)
ing2=st.selectbox("Ingredient 2",["None"]+dairy_options)
ing3=st.selectbox("Ingredient 3",["None"]+dairy_options)

selected=[i for i in [ing1,ing2,ing3] if i!="None"]

if len(selected)!=len(set(selected)):
    st.error("Duplicate ingredients not allowed")
    st.stop()

powders=["SMP","WMP","SCM"]

if sum(i in powders for i in selected)>1:
    st.error("Only one of SMP/WMP/SCM allowed in basic version")
    st.stop()

ingredients=[]

for name in selected:

    st.markdown(f"### {name} Composition")

    fat=st.number_input(f"{name} Fat (%)",key=name+"fat")
    snf=st.number_input(f"{name} MSNF (%)",key=name+"snf")
    sugar=st.number_input(f"{name} Sugar (%)",key=name+"sugar")

    ingredients.append({
    "name":name,
    "fat":fat/100,
    "snf":snf/100,
    "sugar":sugar/100
    })

st.markdown('</div>',unsafe_allow_html=True)

# ===================== FRUIT =====================

st.markdown('<div class="card">',unsafe_allow_html=True)
st.markdown('<div class="section-title">Fruit</div>',unsafe_allow_html=True)

fruit_percent=st.number_input("Fruit % of Mix")
fruit_fat_percent=st.number_input("Fruit Fat (%)")
fruit_snf_percent=st.number_input("Fruit SNF (%)")
fruit_sugar_percent=st.number_input("Fruit Sugar (%)")

st.markdown('</div>',unsafe_allow_html=True)

# ===================== STABILIZER =====================

st.markdown('<div class="card">',unsafe_allow_html=True)
st.markdown('<div class="section-title">Stabilizer</div>',unsafe_allow_html=True)

stab_percent=st.number_input("Stabilizer %")
stab_ts=st.number_input("Stabilizer TS (%)")

st.markdown('</div>',unsafe_allow_html=True)

# ===================== EMULSIFIER =====================

st.markdown('<div class="card">',unsafe_allow_html=True)
st.markdown('<div class="section-title">Emulsifier</div>',unsafe_allow_html=True)

emul_percent=st.number_input("Emulsifier Active %")
emul_ts=st.number_input("Emulsifier TS (%)")
emul_fat_percent=st.number_input("Emulsifier Fat (%)")

solve=st.button("Calculate Formulation")

if solve:
    st.markdown(
        """
        <script>
        window.location.href="#result";
        </script>
        """,
        unsafe_allow_html=True
        )

st.markdown('</div>',unsafe_allow_html=True)

# ===================== SOLVER =====================



if solve and T>0 and len(ingredients)>0:

    try:
        
        
            

            

            for ing in ingredients:
                if ing["fat"]==0 and ing["snf"]==0 and ing["sugar"]==0:
                    st.error(f"{ing['name']} composition cannot be all zero.")
                    st.stop()
            with st.spinner("Formulating mix... Please wait"):
                import time
                time.sleep(2)
            fat_required=T*fat_target/100
            snf_required=T*snf_target/100
            sugar_required=T*sugar_target/100

            fruit_qty=fruit_percent*T/100
            fruit_fat=fruit_qty*fruit_fat_percent/100
            fruit_snf=fruit_qty*fruit_snf_percent/100
            fruit_sugar=fruit_qty*fruit_sugar_percent/100

            stab_active=stab_percent*T/100
            stab_actual=stab_active/(stab_ts/100) if stab_ts>0 else 0

            emul_active=emul_percent*T/100
            emul_actual=emul_active/(emul_ts/100) if emul_ts>0 else 0
            emul_fat_kg=emul_actual*emul_fat_percent/100

            n=len(ingredients)

            A=[]
            B=[]

            A.append([ing["fat"] for ing in ingredients])
            B.append(fat_required-fruit_fat-emul_fat_kg)

            if n>=2:
                A.append([ing["snf"] for ing in ingredients])
                B.append(snf_required-fruit_snf)

            if n>=3:
                coeffs=[1-ing["sugar"] for ing in ingredients]
                A.append(coeffs)
                B.append(T-sugar_required+fruit_sugar-fruit_qty-stab_actual-emul_actual)

            A=np.array(A)
            B=np.array(B)

            if np.linalg.matrix_rank(A)<n:
                st.error("System Cannot Solve – CHECK INPUTS")
                st.stop()

            if np.linalg.cond(A) > 100:
                st.error("Unstable system: Ingredient Compositions too Similar.")
                st.stop()

            solution=np.linalg.solve(A,B)

            results={}

            for i,ing in enumerate(ingredients):
                results[ing["name"]]=solution[i]

                

            for name,qty in results.items():
                if qty < -0.001:
                    st.error(
                    f"Invalid formulation: {name} quantity became negative ({qty:.3f} kg)."
                    )
                    st.stop()

            for name,qty in results.items():
                if qty > 0.95*T:
                    st.warning(f"{name} dominates formulation (>95% of batch).")

            added_sugar=sugar_required-(sum(results[name]*ing["sugar"]
            for name,ing in zip(results.keys(),ingredients))+fruit_sugar)
                

            if added_sugar<-0.0001:
                st.error("Intrinsic sugar exceeds target sugar")
                st.stop()

            total_used=(sum(results.values())+
            added_sugar+
            fruit_qty+
            stab_actual+
            emul_actual)

            water=T-total_used

            st.session_state["results"]=results
            st.session_state["added_sugar"]=added_sugar
            st.session_state["fruit_qty"]=fruit_qty
            st.session_state["stab_actual"]=stab_actual
            st.session_state["emul_actual"]=emul_actual
            st.session_state["water"]=water
            st.session_state["T"]=T
            

            if water<-0.0001:
                st.error("Formulation exceeds total batch size")
                st.stop()

            total_solids=fat_required+snf_required+sugar_required+stab_active+emul_active

            ts_percent=(total_solids/T)*100
            water_percent=(water/T)*100

            k1,k2=st.columns(2)

            with k1:
                st.markdown(f"""
                <div class="kpi-card">
                <div class="kpi-number">{ts_percent:.2f}%</div>
                <div class="kpi-label">Total Solids</div>
                </div>
                """,unsafe_allow_html=True)

            with k2:
                st.markdown(f"""
                <div class="kpi-card">
                <div class="kpi-number">{water_percent:.2f}%</div>
                <div class="kpi-label">Water</div>
                </div>
                """,unsafe_allow_html=True)

            st.markdown('<div class="card">',unsafe_allow_html=True)
            st.markdown('<div class="section-title">Ingredient Breakdown</div>',unsafe_allow_html=True)

            grid_html='<div class="breakdown-grid">'

            for name,qty in results.items():

                grid_html+=f'<div class="breakdown-item"><b>{name}</b></div>'
                grid_html+=f'<div class="breakdown-item">{qty:.3f} kg</div>'

            grid_html+=f'<div class="breakdown-item"><b>Added Sugar</b></div><div class="breakdown-item">{added_sugar:.3f} kg</div>'
            grid_html+=f'<div class="breakdown-item"><b>Fruit</b></div><div class="breakdown-item">{fruit_qty:.3f} kg</div>'
            grid_html+=f'<div class="breakdown-item"><b>Stabilizer</b></div><div class="breakdown-item">{stab_actual:.3f} kg</div>'
            grid_html+=f'<div class="breakdown-item"><b>Emulsifier</b></div><div class="breakdown-item">{emul_actual:.3f} kg</div>'
            grid_html+=f'<div class="breakdown-item"><b>Water</b></div><div class="breakdown-item">{water:.3f} kg</div>'

            grid_html+='</div>'

            st.markdown(grid_html,unsafe_allow_html=True)
            st.markdown('</div>',unsafe_allow_html=True)

            st.markdown('<div class="card">',unsafe_allow_html=True)
            

            st.markdown('<div class="card">',unsafe_allow_html=True)
            st.subheader("Advanced Quality Insight")

            if fat_target<6:
                st.error("Critical: Fat below 6% – Hard pack structural instability likely.")
            elif 6<=fat_target<8:
                st.warning("Moderate Risk: Low fat – Light body expected.")
            elif 8<=fat_target<=12:
                st.success("Good fat range – Creamy body expected.")
            elif fat_target>14:
                st.warning("High fat – Heavy body risk.")

            if sugar_target<12:
                st.warning("Low sugar – Hard texture risk.")
            elif 12<=sugar_target<=16:
                st.success("Balanced sugar range.")
            elif 16<sugar_target<=18:
                st.warning("High sugar – Soft body risk.")
            elif sugar_target>18:
                st.error("Critical: Excess sugar – Freezing point depression risk.")

            if fat_target>0:
                ratio=sugar_target/fat_target
                if ratio>3:
                    st.error("Sugar-to-fat ratio too high – Collapse risk.")
                elif 2.2<=ratio<=3:
                    st.warning("High sugar relative to fat.")
                elif 1.3<=ratio<2.2:
                    st.success("Healthy fat-sugar balance.")

            if snf_target>12.5:
                st.error("High SNF – Lactose crystallization risk.")
            elif 11<=snf_target<=13:
                st.warning("Elevated SNF – Monitor lactose stability.")
            elif 8<=snf_target<11:
                st.success("Safe SNF range.")

            if ts_percent<32:
                st.error("Very low solids – Icy texture risk.")
            elif 32<=ts_percent<35:
                st.warning("Low solids – Slight iciness possible.")
            elif 35<=ts_percent<=40:
                st.success("Balanced commercial mix.")
            elif ts_percent>42:
                st.warning("High solids – Dense mix.")

            if water_percent<2:
                st.warning("Low water buffer.")
            elif water_percent>65:
                st.warning("High water dilution risk.")
            else:
                st.success("Water level within safe range.")

            st.markdown('</div>',unsafe_allow_html=True)

    except:

        st.error("System Cannot Solve – Check Inputs")


st.markdown("---")
st.markdown(
"<center><b>Made with ❤️ by Jatin Thakral and Kanan Thakral</b></center>",
unsafe_allow_html=True
)