import matplotlib
import matplotlib.ticker
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import requests
import os

sns.set(style='dark')

script_dir = os.path.dirname(os.path.abspath(__file__))  # Get script directory
dataset_day = pd.read_csv(os.path.join(script_dir, "dataset_day_clean.csv"))
dataset_hour = pd.read_csv(os.path.join(script_dir, "dataset_hour_clean.csv"))

datetime_columns = ["date"]
dataset_day.sort_values(by="date", inplace=True)
dataset_day.reset_index(inplace=True)   

dataset_hour.sort_values(by="date", inplace=True)
dataset_hour.reset_index(inplace=True)

for column in datetime_columns:
    dataset_day[column] = pd.to_datetime(dataset_day[column])
    dataset_hour[column] = pd.to_datetime(dataset_hour[column])

min_date_days = dataset_day["date"].min()
max_date_days = dataset_day["date"].max()

min_date_hour = dataset_hour["date"].min()
max_date_hour = dataset_hour["date"].max()

for column in datetime_columns:
    dataset_day[column] = pd.to_datetime(dataset_day[column])
    dataset_hour[column] = pd.to_datetime(dataset_hour[column])
with st.sidebar:
    # Menambahkan logo perusahaan
    # iamge ID
    file_id = "1toYJcJYmIzk57l0E6ArDqFooidA92w1Q"

    # URL
    url = f"https://drive.google.com/uc?export=view&id={file_id}"
    response = requests.get(url)
    st.image(response.content)

        # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date_days,
        max_value=max_date_days,
        value=[min_date_days, max_date_days])
  
date_df_days = dataset_day[(dataset_day["date"] >= str(start_date)) & 
                       (dataset_day["date"] <= str(end_date))]

date_df_hour = dataset_hour[(dataset_hour["date"] >= str(start_date)) & 
                        (dataset_hour["date"] <= str(end_date))]



def count_by_day_df(day_df):
    day_df_count_2011 = day_df.query(str('date >= "2011-01-01" and date < "2012-12-31"'))
    return day_df_count_2011

def total_registered_df(day_df):
   reg_df =  day_df.groupby(by="date").agg({
      "registered": "sum"
    })
   reg_df = reg_df.reset_index()
   reg_df.rename(columns={
        "registered": "register_sum"
    }, inplace=True)
   return reg_df

def total_casual_df(day_df):
   cas_df =  day_df.groupby(by="date").agg({
      "casual": ["sum"]
    })
   cas_df = cas_df.reset_index()
   cas_df.rename(columns={
        "casual": "casual_sum"
    }, inplace=True)
   return cas_df

def hour_sum(dataset_hour):
    grouped_data = dataset_hour.groupby(["workingday", "hour"]).agg({"count_rental": "sum"})

    # Reset index to bring 'workingday' and 'hour' back as columns
    grouped_data = grouped_data.reset_index()
    # Convert 'hour' to categorical to prevent unnecessary spacing
    grouped_data["hour"] =grouped_data["hour"].astype(str)

    # Filter only workdays and get the top 5 busiest hours
    top_hours_workday = grouped_data[grouped_data["workingday"] == "Workday"].nlargest(5, "count_rental")

    bottom_hours_workday = grouped_data[grouped_data["workingday"] == "Workday"].nsmallest(5, "count_rental")

    top_hours_holiday = grouped_data[grouped_data["workingday"] == "Holiday"].nlargest(5, "count_rental")
    bottom_hours_holiday = grouped_data[grouped_data["workingday"] == "Holiday"].nsmallest(5, "count_rental")
    
    return top_hours_holiday, bottom_hours_holiday, top_hours_workday, bottom_hours_workday

def sum_order (dataset_hour):
    sum_order_items_df = dataset_hour.groupby("hour").count_rental.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

def macem_season (day_df): 
    season_df = day_df.groupby(by="season").count_rental.sum().reset_index() 
    return season_df



day_df_count_2011 = count_by_day_df(date_df_days)
reg_df = total_registered_df(date_df_days)
cas_df = total_casual_df(date_df_days)



#Melengkapi Dashboard dengan Berbagai Visualisasi Data
st.header('Bike Sharing')

st.subheader('Daily Sharing')
col1, col2, col3 = st.columns(3)
 
with col1:
    total_orders = day_df_count_2011.count_rental.sum()
    st.metric("Total Sharing Bike", value=total_orders)

with col2:
    total_sum = reg_df.register_sum.sum()
    st.metric("Total Registered", value=total_sum)

with col3:
    total_sum = cas_df.casual_sum.sum()
    st.metric("Total Casual", value=total_sum)



### Pertanyaan 1 ==================================================================================================
# Menampilkan subjudul untuk hari kerja
st.subheader("Pada jam berapa pada hari kerja penyewaan paling banyak dan paling sedikit?")

# Menghitung jumlah penyewaan berdasarkan hari kerja dan jam
top_hours_holiday, bottom_hours_holiday, top_hours_workday, bottom_hours_workday = hour_sum(date_df_hour)

# Membuat figure untuk hari kerja dengan ukuran 15x5
fig_workday, axes_workday = plt.subplots(1, 2, figsize=(15, 5))

# Bar chart untuk 5 jam dengan penyewaan terbanyak pada hari kerja
sns.barplot(
    x="hour", 
    y="count_rental", 
    data=top_hours_workday,  
    palette=["#FF4500"] + ["#D3D3D3"] * 4,  
    ax=axes_workday[0]
)
axes_workday[0].set_xlabel("Jam")
axes_workday[0].set_ylabel("Total Penyewaan")
axes_workday[0].set_title("5 Jam Tersibuk pada Hari Kerja")

# Bar chart untuk 5 jam dengan penyewaan tersedikit pada hari kerja
sns.barplot(
    x="hour", 
    y="count_rental", 
    data=bottom_hours_workday,  
    palette=["#FF4500"] + ["#D3D3D3"] * 4,  
    ax=axes_workday[1]
)
axes_workday[1].set_xlabel("Jam")
axes_workday[1].set_ylabel("Total Penyewaan")
axes_workday[1].set_title("5 Jam Tersepi pada Hari Kerja")

# Menyesuaikan tata letak dan menampilkan plot di Streamlit
plt.tight_layout()
st.pyplot(fig_workday)

# Menampilkan subjudul untuk hari libur
st.subheader("Pada jam berapa pada hari libur penyewaan paling banyak dan paling sedikit?")

# Membuat figure untuk hari libur dengan ukuran 15x5
fig_holiday, axes_holiday = plt.subplots(1, 2, figsize=(15, 5))

# Bar chart untuk 5 jam dengan penyewaan terbanyak pada hari libur
sns.barplot(
    x="hour", 
    y="count_rental", 
    data=top_hours_holiday,  
    palette=["#FF4500"] + ["#D3D3D3"] * 4,  
    ax=axes_holiday[0]
)
axes_holiday[0].set_xlabel("Jam")
axes_holiday[0].set_ylabel("Total Penyewaan")
axes_holiday[0].set_title("5 Jam Tersibuk pada Hari Libur")

# Bar chart untuk 5 jam dengan penyewaan tersedikit pada hari libur
sns.barplot(
    x="hour", 
    y="count_rental", 
    data=bottom_hours_holiday,  
    palette=["#FF4500"] + ["#D3D3D3"] * 4,  
    ax=axes_holiday[1]
)
axes_holiday[1].set_xlabel("Jam")
axes_holiday[1].set_ylabel("Total Penyewaan")
axes_holiday[1].set_title("5 Jam Tersepi pada Hari Libur")

# Menyesuaikan tata letak dan menampilkan plot di Streamlit
plt.tight_layout()
st.pyplot(fig_holiday)

### End pertanyaan 1 ==================================================================================================


###  pertanyaan 2 ==================================================================================================
st.subheader("Bagaimana perbedaan jumlah penyewaan sepeda pada hari libur dan hari kerja ?")


# Mengelompokkan data berdasarkan hari kerja dan menghitung total penyewaan
df = date_df_days.groupby("workingday")[["count_rental"]].sum()

# Menyiapkan label dan ukuran secara dinamis
labels = df.index  # ["Workday", "Holiday"]
sizes = df["count_rental"]  # Total penyewaan untuk setiap kategori

# Memberikan efek pemisahan pada salah satu bagian
explode = (0, 0.05)

# Membuat figure dan pie chart
fig, ax = plt.subplots(figsize=(7, 7))
ax.pie(
    sizes, 
    explode=explode, 
    labels=labels, 
    autopct='%1.1f%%', 
    colors=["#FF4500","#D3D3D3"], 
    shadow=True, 
    startangle=90
)

# Menjaga bentuk pie chart agar tetap bulat
ax.axis('equal')
st.pyplot(fig)
### End pertanyaan 2 ==================================================================================================

###  pertanyaan 3 ==================================================================================================
 
st.subheader("Musim mana yang memiliki penyewaan sepeda paling banyak?")

# Mengelompokkan data berdasarkan musim dan menghitung total penyewaan
df = date_df_days.groupby("season", observed=False)["count_rental"].sum().reset_index()

# Menentukan nilai maksimum untuk sumbu Y
df = df.sort_values(by="count_rental", ascending=False)
max_rental = df["count_rental"].max()

# Membuat figure dan barplot
fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(
    x="season", 
    y="count_rental", 
    data=df, 
    palette=["#FF4500", "#D3D3D3", "#D3D3D3", "#D3D3D3"], 
    ci=None
)

# Menyesuaikan batas sumbu Y agar lebih proporsional
plt.ylim(0, max_rental * 1.03)

# Mengatur format angka pada sumbu Y agar lebih mudah dibaca
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))

# Menambahkan label dan judul
plt.xlabel("Musim", fontsize=25, labelpad=15)
plt.ylabel("Total Penyewaan", fontsize=25, labelpad=15)
plt.title("Total Penyewaan Sepeda Berdasarkan Musim", fontsize=30, pad=20)

# Menyesuaikan ukuran label sumbu
ax.tick_params(axis='x', labelsize=20)
ax.tick_params(axis='y', labelsize=20)

st.pyplot(fig)
### End pertanyaan 3 ==================================================================================================

### pertanyaan 4 ==================================================================================================
st.subheader("Apakah suhu mempengaruhi jumlah penyewa sepeda ?")

dataset_suhu = date_df_hour.groupby(by=["temp"], observed=False).agg({
    "count_rental": ["sum"],
}).reset_index()
dataset_suhu.columns = ["temp", "count_rental"]

# Membuat bar chart
fig, ax = plt.subplots(figsize=(10, 8))
sns.barplot(x="temp", y="count_rental", data=dataset_suhu, palette=["#ADD8E6", "#fff082", "#eb9234"], ax=ax)

# Mengatur format angka pada sumbu Y agar lebih mudah dibaca (dengan pemisah ribuan)
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
# Menambahkan label dan judul
plt.xlabel("Kategori Suhu", fontsize=14)
plt.ylabel("Total Penyewaan", fontsize=14)
plt.title("Total Penyewaan Sepeda Berdasarkan Suhu", fontsize=16)
st.pyplot(fig)
### End pertanyaan 4 ==================================================================================================


###  pertanyaan 5 ==================================================================================================

st.subheader("Performa penyewaan sepeda perusahaan periode 2011-2012")
fig = plt.figure(figsize=(24, 14))

# Menghitung jumlah penyewaan maksimum per hari
df = date_df_days.groupby("date")["count_rental"].max()

# Membuat scatter plot dan line plot dengan warna oranye kemerahan
plt.scatter(df.index, df.values, c="#FF4500", s=10, marker='o', label="Maksimum Harian")
plt.plot(df.index, df.values, color="#FF4500")

# Menambahkan label dan judul dan memperbesar tick x dan tick y

plt.xlabel("Tanggal", fontsize=19)
plt.ylabel("Jumlah Penyewaan", fontsize=19)
plt.xticks(fontsize=17)
plt.yticks(fontsize=17)

st.pyplot(fig)
### End pertanyaan 5 ==================================================================================================
