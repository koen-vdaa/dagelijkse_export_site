import json, datetime, pathlib, random

# 1) Bereken/haal je data op (hier een demo-getal)
result = {
    "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
    "random_value": random.randint(1, 100)
}

# 2) Schrijf naar de 'site' map (dit wordt je publieke website)
pathlib.Path("site").mkdir(exist_ok=True)

with open("site/data.json", "w") as f:
    json.dump(result, f, indent=2)

# 3) Maak simpele HTML die data.json ophaalt
with open("site/index.html", "w") as f:
    f.write("""<!doctype html>
<html lang="nl">
<head>
  <meta charset="utf-8">
  <title>Dagelijkse resultaten</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <style>body{font-family:system-ui,Arial;margin:2rem;max-width:60ch}</style>
</head>
<body>
  <h1>Dagelijkse resultaten</h1>
  <p>Deze pagina wordt dagelijks automatisch bijgewerkt.</p>
  <pre id="out">laden…</pre>
  <script>
  fetch('data.json')
    .then(r => r.json())
    .then(d => { document.getElementById('out').textContent = JSON.stringify(d, null, 2); })
    .catch(err => { document.getElementById('out').textContent = 'Fout bij laden: ' + err; });
  </script>
</body>
</html>""")
