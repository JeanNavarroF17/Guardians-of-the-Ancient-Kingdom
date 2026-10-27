"""Casos de prueba de Guardians of the Ancient Kingdom (ejecución: python main.py)."""

from personajes import (Arquero, AtaqueInvalidoError, Combate, Guerrero, Mago,
                        Personaje)


def titulo(n, texto):
    print(f"\n{'=' * 60}\nCaso {n}: {texto}\n{'=' * 60}")


def comprobar(descripcion, condicion):
    print(f"  [{'OK' if condicion else 'FALLÓ'}] {descripcion}")


def rechaza(descripcion, funcion, excepcion=(ValueError, TypeError)):
    try:
        funcion()
    except excepcion as e:
        print(f"  [OK] {descripcion} -> {type(e).__name__}: {e}")
    else:
        print(f"  [FALLÓ] {descripcion} no lanzó excepción")


def main():
    titulo(1, "Creación correcta de los tres tipos de personajes")
    g = Guerrero("Arthas", 100, 30, 20)
    m = Mago("Gandalf", 80, 40, 10)
    a = Arquero("Legolas", 90, 35, 15)
    for p in (g, m, a):
        print(" ", p.mostrar_estado())
    comprobar("Los tres son Personaje", all(isinstance(p, Personaje) for p in (g, m, a)))
    rechaza("Instanciar la clase abstracta Personaje", lambda: Personaje("X", 10, 10, 10), TypeError)

    titulo(2, "Rechazo de vida superior a 100 o negativa")
    rechaza("Vida 101", lambda: Guerrero("A", 101, 10, 5))
    rechaza("Vida -5", lambda: Mago("A", -5, 10, 5))

    titulo(3, "Rechazo de nombres vacíos")
    rechaza("Nombre ''", lambda: Arquero("", 50, 10, 5))
    rechaza("Nombre '   '", lambda: Arquero("   ", 50, 10, 5))

    titulo(4, "Rechazo de ataques y defensas inválidos")
    rechaza("Ataque 0", lambda: Guerrero("A", 50, 0, 5))
    rechaza("Ataque negativo", lambda: Guerrero("A", 50, -3, 5))
    rechaza("Defensa negativa", lambda: Mago("A", 50, 10, -1))
    rechaza("Ataque como texto", lambda: Mago("A", 50, "10", 1))

    titulo(5, "Habilidad del Guerrero (ataque 30 x 1.2 - defensa 10 = 26)")
    guerrero = Guerrero("Arthas", 100, 30, 20)
    objetivo = Mago("Objetivo", 100, 10, 10)
    danio = guerrero.atacar(objetivo)
    print(f"  Daño causado: {danio} | Vida objetivo: {objetivo.vida}")
    comprobar("Daño esperado 26", danio == 26 and objetivo.vida == 74)

    titulo(6, "Ataque del Mago ignora la defensa (ataque 40, defensa 20 -> 40)")
    mago = Mago("Gandalf", 80, 40, 10)
    objetivo = Guerrero("Tanque", 100, 10, 20)
    danio = mago.atacar(objetivo)
    print(f"  Daño causado: {danio} | Vida objetivo: {objetivo.vida}")
    comprobar("Daño esperado 40", danio == 40 and objetivo.vida == 60)

    titulo(7, "Disparo crítico del Arquero (35 - 15 = 20, x2 = 40)")
    arquero = Arquero("Legolas", 90, 35, 15)
    objetivo = Guerrero("Objetivo", 100, 10, 15)
    danio = arquero.atacar(objetivo)
    print(f"  Daño causado: {danio} | Vida objetivo: {objetivo.vida}")
    comprobar("Daño esperado 40", danio == 40 and objetivo.vida == 60)
    debil = Arquero("Novato", 50, 10, 5)
    muro = Guerrero("Muro", 100, 10, 10)
    comprobar("Ataque no supera defensa -> daño 0", debil.atacar(muro) == 0)

    titulo(8, "Imposible tener vida negativa")
    p = Guerrero("Frágil", 20, 10, 5)
    recibido = p.recibir_danio(50)
    print(f"  Daño pedido: 50 | Daño efectivo: {recibido} | Vida: {p.vida}")
    comprobar("Vida queda en 0 y daño efectivo 20", p.vida == 0 and recibido == 20)
    rechaza("Daño negativo", lambda: p.recibir_danio(-1))
    rechaza("Asignar vida -1 con el setter", lambda: setattr(p, "vida", -1))

    titulo(9, "Imposible atacar estando derrotado")
    muerto = Mago("Caído", 50, 30, 5)
    muerto.recibir_danio(50)
    vivo = Guerrero("Vivo", 50, 30, 5)
    rechaza("Derrotado ataca", lambda: muerto.atacar(vivo), AtaqueInvalidoError)
    rechaza("Atacar a un derrotado", lambda: vivo.atacar(muerto), AtaqueInvalidoError)
    rechaza("Objetivo no válido (None)", lambda: vivo.atacar(None), AtaqueInvalidoError)

    titulo(10, "Combate completo: Arthas (Guerrero) vs Gandalf (Mago)")
    arthas = Guerrero("Arthas", 100, 30, 20)
    gandalf = Mago("Gandalf", 80, 40, 10)
    combate = Combate(arthas, gandalf)
    ganador = combate.iniciar()

    titulo(11, "Identificación correcta del ganador")
    print(f"  Ganador: {ganador.nombre if ganador else 'ninguno'}")
    comprobar("Gana Gandalf", ganador is gandalf)
    comprobar("Arthas derrotado (vida 0) y Gandalf con 2", arthas.vida == 0 and gandalf.vida == 2)

    titulo(12, "Empate técnico (ronda sin daño)")
    a1 = Arquero("Arquero A", 100, 10, 50)
    a2 = Arquero("Arquero B", 100, 10, 50)
    combate = Combate(a1, a2)
    ganador = combate.iniciar()
    comprobar("No hay ganador", ganador is None)
    comprobar("Se declaró empate", combate.empate)
    comprobar("Terminó en la primera ronda", combate.rondas == 1)

    print("\nFin de los casos de prueba.")


if __name__ == "__main__":
    main()
