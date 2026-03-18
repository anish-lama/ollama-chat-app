import google.generativeai as genai

genai.configure(
    api_key="AIzaSyDuhrUto39lhRA2xJu-4a4Pcd1dxttwZ-s",
    transport="rest"   # 👈 THIS IS THE FIX
)

model = genai.GenerativeModel("gemini-1.5-flash")

response = model.generate_content("Say hello")

print(response.text)