import time, random
import datetime, requests
print("ARRANCANDO...")
print("="*52)
print("  TERMINAL PRO  |  SOLANA MEMECOINS  |  LIVE")
print("="*52)
CAP = 50
PCT = 0.20
VOL_MIN = 100000
MAX_OP = 2
def g(d, k):
 v = d.get(k)
 if v is None:
  return 0
 return v
class Ayudante:
 def __init__(self, tipo):
  self.tipo = tipo
 def votar(self, m):
  if self.tipo == "vol":
   return m['vol']
  if self.tipo == "mom":
   return m['c1']*1000 + m['c5']*500
  if self.tipo == "riesgo":
   return -abs(m['c5'])*1000 + m['vol']*0.1
  return 0
class Bot:
 def __init__(self, n):
  self.n = n
  self.saldo = CAP
  self.ab = []
  self.ops = 0
  self.equipo = [Ayudante("vol"), Ayudante("mom"), Ayudante("riesgo")]
 def ok(self, m):
  # Objetivo: multiplicar sin quedar en 0
  if self.saldo <= 1:
   return False
  if len(self.ab) >= MAX_OP:
   return False
  if m['precio'] <= 0:
   return False
  return True
 def elegir_mejor(self, todas):
  # Ven TODO el scan, ellos eligen segun estrategia
  candidatos = [m for m in todas if self.ok(m)]
  if not candidatos:
   return None
  def puntaje(m):
   total = 0
   for ay in self.equipo:
    total += ay.votar(m)
   if self.n == "BOT 20":
    total += m.get('score',0)*0.01
   elif self.n == "BOT 1":
    total += -abs(m['c5'])*2000
   else:
    total += m['c1']*1500
   return total
  return max(candidatos, key=puntaje)
 def buy(self, m):
  # Ellos deciden cuanto meter segun confianza
  confianza = 0
  for ay in self.equipo:
   confianza += ay.votar(m)
  if confianza > 500000:
   pct_usar = 1.0
   modo = "ALL-IN"
  elif confianza > 200000:
   pct_usar = 0.50
   modo = "50%"
  else:
   pct_usar = PCT
   modo = "20% PASO A PASO"
  monto = self.saldo * pct_usar
  # Nunca quedar en 0, dejar $1
  if monto >= self.saldo:
   monto = self.saldo - 1
  if monto <= 0:
   return
  self.saldo -= monto
  o = {'nom': m['nom'], 'monto': monto, 'pe': m['precio'], 'ca': m['ca'], 't': time.time()}
  self.ab.append(o)
  print(f"  [+] {self.n}  COMPRA {m['nom']} [{m['fuente']}]  ${monto:.2f} [{modo}]")
  print(f"      CA: {m['ca']}")
 def sell(self):
  for o in self.ab[:]:
   var = random.uniform(-0.10, 0.15)
   if var <= -0.08 or var >= 0.12:
    mot = "SL -8%" if var <= -0.08 else "TP +12%"
    gan = o['monto']*var
    self.saldo += o['monto'] + gan
    self.ops += 1
    self.ab.remove(o)
    signo = "+" if gan >= 0 else ""
    print(f"  [-] {self.n}  VENTA {o['nom']}  {mot}  {signo}${gan:.2f}")
bots = [Bot("BOT 1"), Bot("BOT 2"), Bot("BOT 20")]
def scan():
 res = []
 heads = {"User-Agent": "Mozilla/5.0"}
 try:
  u = "https://api.dexscreener.com/token-profiles/latest/v1"
  r = requests.get(u, headers=heads, timeout=15)
  if r.status_code != 200:
   print(f"DEX Rate Limit {r.status_code} - esperando...")
   time.sleep(5)
   return res
  if not r.text.strip():
   return res
  data = r.json()
  cas = [tok.get('tokenAddress','') for tok in data if tok.get('tokenAddress')]
  if not cas:
   return res
  u2 = "https://api.dexscreener.com/latest/dex/tokens/" + ",".join(cas[:30])
  r2 = requests.get(u2, headers=heads, timeout=15)
  if r2.status_code != 200 or not r2.text.strip():
   return res
  j2 = r2.json()
  pairs = j2.get('pairs', [])
  for pair in pairs:
   if pair.get('chainId') != 'solana':
    continue
   did = pair.get('dexId', '')
   fuente = 'PUMP' if 'pump' in did.lower() else 'DEX'
   bt = pair.get('baseToken', {})
   ca = bt.get('address','')
   pc = pair.get('priceChange', {})
   vol = pair.get('volume', {})
   m = {'nom': bt.get('symbol','?'), 'precio': float(g(pair,'priceUsd')), 'c5': float(g(pc,'m5')), 'c1': float(g(pc,'h1')), 'vol': float(g(vol,'h24')), 'ca': ca, 'fuente': fuente}
   res.append(m)
 except Exception as e:
  print("Error DEX: " + str(e))
 return res
print("BOT FAVORABLES INICIADO - SOLO INVERTIR YA")
print("-"*52)
while True:
 todas = scan()
 fav_todas = []
 for m in todas:
  if m['c5'] >= -5 and m['c5'] <= 25 and m['c1'] >= 20 and m['vol'] >= VOL_MIN:
   m['score'] = m['vol']*(1+m['c1']/100)
   fav_todas.append(m)
  else:
   m['score'] = m['vol']*(1+m['c1']/100) if m['c1'] > 0 else m['vol']
 fav_todas = sorted(fav_todas, key=lambda x: x['score'], reverse=True)
 fav_mostrar = fav_todas[:3]
 ahora = datetime.datetime.now().strftime("%H:%M:%S")
 print("")
 print(f"  TOP 3 FAVORABLES  |  {ahora}  |  SCAN: {len(todas)}  |  FAV: {len(fav_todas)}")
 print("-"*52)
 if len(fav_mostrar) == 0:
  print("  Sin oportunidades favorables - Esperando 60s...")
 else:
  print(f"  {'#':<3} {'TOKEN':<12} {'SRC':<5} {'PRECIO':<12} {'5m':<8} {'1h':<8} {'VOL 24H':<10}")
  print("-"*52)
  for i, m in enumerate(fav_mostrar):
   nom = m['nom'][:11]
   print(f"  {i+1:<3} {nom:<12} {m['fuente']:<5} ${m['precio']:<11.6g} {m['c5']:+.2f}%  {m['c1']:+.2f}%  ${m['vol']:,.0f}")
   print(f"      CA: {m['ca']}")
 print("-"*52)
 print("  PORTAFOLIO")
 for b in bots:
  print(f"  {b.n:<8} Saldo: ${b.saldo:>7.2f}  Abiertas: {len(b.ab)}  Ops: {b.ops}")
 print("="*52)
 for bot in bots:
  mejor = bot.elegir_mejor(todas)
  if mejor:
   pr = 0.7 if bot.n == "BOT 20" else 0.3
   if random.random() < pr:
    bot.buy(mejor)
    print(f"      -> {bot.n} eligio {mejor['nom']} por mejor conveniencia")
  bot.sell()
 time.sleep(60)
