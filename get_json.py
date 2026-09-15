import requests, json

url = "https://app.parlamento.pt/webutils/docs/doc.txt?path=jKh9rFwHv%2bx9gIyMsPvsYvx8y08lTTdX5N3fIVcXtzLHJJI9lXA0859yPrORpjjGAe3UH5%2fO4Rn7G%2fAJevGOytrBriwO%2bMTQuCgbxQb2dS%2bJu%2bsXyklOlaB81BNSWVYNcUtv2qKZM37dfGssaoXgh0aQWvOHwfchmt%2bm1UxVZh4Ir8%2boZ08RaSRBN9aPfu%2f%2fKrOk38CzEhjAG6bjc1nlOkT8XMmunC%2flX91AoF0qh%2fOiihtGlp6DKJzC9gi4PnoYO7JjiyKKyW8JeJRcBBRX2zFhV0gXx%2bBTM8Is7rt8Ap5Ffv6kkZE8QRETfDVmFMfGvE1isuFpVr%2bsCrUejgQxI4Tg%2fExM%2bDX1Ftm2HONuKoY%3d&fich=IniciativasXVII_json.txt&Inline=true"  # o teu URL
r = requests.get(url)
data = r.json()  # em vez de r.text[:15000]

with open("data/iniciativas_raw.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False)