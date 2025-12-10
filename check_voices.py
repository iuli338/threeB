import asyncio
import edge_tts

async def main():
    voices = await edge_tts.list_voices()
    print("--- VOCI ROMÂNEȘTI DISPONIBILE ---")
    found = False
    for v in voices:
        if "ro-RO" in v["ShortName"]:
            print(f"Nume: {v['ShortName']} | Gen: {v['Gender']}")
            found = True
            
    if not found:
        print("ALERTĂ: Nu s-au găsit voci de română! Verifică conexiunea la net.")

if __name__ == "__main__":
    asyncio.run(main())