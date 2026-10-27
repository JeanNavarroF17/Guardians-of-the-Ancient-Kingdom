"""Guardians of the Ancient Kingdom - definición de las clases del sistema.

Este módulo solo define clases: no ejecuta nada al importarse.
"""

from abc import ABC, abstractmethod

MAX_RONDAS = 50


class AtaqueInvalidoError(ValueError):
    """Se intenta un ataque que rompe las reglas (atacante/objetivo inválido o derrotado)."""


class Personaje(ABC):
    """Clase abstracta con lo que comparten todos los guardianes."""

    VIDA_MAXIMA = 100

    def __init__(self, nombre, vida, ataque, defensa):
        # Se asigna mediante los setters para reutilizar las validaciones.
        self.nombre = nombre
        self.vida = vida
        self.ataque = ataque
        self.defensa = defensa

    # ---------------- Validación auxiliar ----------------
    @staticmethod
    def _validar_entero(valor, campo):
        # bool es subclase de int, pero no es un valor numérico válido aquí.
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise TypeError(f"{campo} debe ser un entero, se recibió {type(valor).__name__}.")

    # ---------------- Nombre ----------------
    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str):
            raise TypeError("El nombre debe ser texto.")
        if not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        self.__nombre = valor.strip()

    # ---------------- Vida ----------------
    @property
    def vida(self):
        return self.__vida

    @vida.setter
    def vida(self, valor):
        self._validar_entero(valor, "La vida")
        if not 0 <= valor <= self.VIDA_MAXIMA:
            raise ValueError(f"La vida debe estar entre 0 y {self.VIDA_MAXIMA}.")
        self.__vida = valor

    # ---------------- Ataque ----------------
    @property
    def ataque(self):
        return self.__ataque

    @ataque.setter
    def ataque(self, valor):
        self._validar_entero(valor, "El ataque")
        if valor <= 0:
            raise ValueError("El ataque debe ser un entero positivo.")
        self.__ataque = valor

    # ---------------- Defensa ----------------
    @property
    def defensa(self):
        return self.__defensa

    @defensa.setter
    def defensa(self, valor):
        self._validar_entero(valor, "La defensa")
        if valor < 0:
            raise ValueError("La defensa no puede ser negativa.")
        self.__defensa = valor

    # ---------------- Comportamiento común ----------------
    def recibir_danio(self, cantidad):
        """Resta vida (nunca por debajo de 0) y devuelve el daño efectivamente recibido.

        La cantidad ya viene calculada: aquí NO se vuelve a descontar la defensa.
        """
        self._validar_entero(cantidad, "El daño")
        if cantidad < 0:
            raise ValueError("El daño no puede ser negativo.")
        efectivo = min(cantidad, self.__vida)
        self.__vida -= efectivo
        return efectivo

    def esta_vivo(self):
        return self.__vida > 0

    def mostrar_estado(self):
        estado = "vivo" if self.esta_vivo() else "derrotado"
        return (f"{self.nombre} ({type(self).__name__}) - Vida: {self.vida} | "
                f"Ataque: {self.ataque} | Defensa: {self.defensa} | {estado}")

    def _validar_ataque(self, objetivo):
        """Validaciones comunes a todos los ataques."""
        if not isinstance(objetivo, Personaje):
            raise AtaqueInvalidoError("El objetivo no es un personaje válido.")
        if objetivo is self:
            raise AtaqueInvalidoError("Un personaje no puede atacarse a sí mismo.")
        if not self.esta_vivo():
            raise AtaqueInvalidoError(f"{self.nombre} está derrotado y no puede atacar.")
        if not objetivo.esta_vivo():
            raise AtaqueInvalidoError(f"{objetivo.nombre} ya está derrotado.")

    @abstractmethod
    def calcular_danio(self, objetivo):
        """Daño que infligiría contra el objetivo (cada guardián lo define distinto)."""

    @abstractmethod
    def atacar(self, objetivo):
        """Ataca al objetivo y devuelve el daño efectivamente causado."""

    def __str__(self):
        return self.mostrar_estado()


class Guerrero(Personaje):
    """Golpe poderoso: ataque +20 % antes de descontar la defensa."""

    def calcular_danio(self, objetivo):
        # ataque * 1.20 con enteros (evita errores de coma flotante); floor.
        potenciado = self.ataque * 120 // 100
        return max(0, potenciado - objetivo.defensa)

    def atacar(self, objetivo):
        self._validar_ataque(objetivo)
        return objetivo.recibir_danio(self.calcular_danio(objetivo))


class Mago(Personaje):
    """Hechizo penetrante: ignora la defensa del objetivo."""

    def calcular_danio(self, objetivo):
        return self.ataque

    def atacar(self, objetivo):
        self._validar_ataque(objetivo)
        return objetivo.recibir_danio(self.calcular_danio(objetivo))


class Arquero(Personaje):
    """Disparo crítico: si ataque > defensa, duplica el daño convencional."""

    def calcular_danio(self, objetivo):
        base = max(0, self.ataque - objetivo.defensa)
        return base * 2 if self.ataque > objetivo.defensa else 0

    def atacar(self, objetivo):
        self._validar_ataque(objetivo)
        return objetivo.recibir_danio(self.calcular_danio(objetivo))


class Combate:
    """Administra un enfrentamiento por turnos entre dos personajes ya creados (agregación)."""

    def __init__(self, personaje1, personaje2, verbose=True):
        for p in (personaje1, personaje2):
            if not isinstance(p, Personaje):
                raise TypeError("Un combate solo admite objetos Personaje.")
        if personaje1 is personaje2:
            raise ValueError("Un combate necesita dos personajes distintos.")
        self.__participantes = (personaje1, personaje2)
        self.__turno = 0              # índice del atacante actual
        self.__rondas = 0
        self.__empate_tecnico = False
        self.__empate_por_rondas = False
        self.verbose = verbose

    # ---------------- Consultas ----------------
    @property
    def participantes(self):
        return self.__participantes

    @property
    def rondas(self):
        return self.__rondas

    @property
    def atacante_actual(self):
        return self.__participantes[self.__turno]

    @property
    def empate(self):
        return self.__empate_tecnico or self.__empate_por_rondas

    def _imprimir(self, texto):
        if self.verbose:
            print(texto)

    # ---------------- Lógica ----------------
    def cambiar_turno(self):
        self.__turno = 1 - self.__turno

    def verificar_ganador(self):
        """Devuelve el personaje vencedor o None si nadie ha ganado todavía."""
        p1, p2 = self.__participantes
        if p1.esta_vivo() and not p2.esta_vivo():
            return p1
        if p2.esta_vivo() and not p1.esta_vivo():
            return p2
        return None

    def iniciar(self):
        """Ejecuta el combate completo y devuelve el ganador (None si hay empate)."""
        p1, p2 = self.__participantes
        self._imprimir(f"=== {p1.nombre} vs {p2.nombre} ===")
        self._imprimir(p1.mostrar_estado())
        self._imprimir(p2.mostrar_estado())

        while self.verificar_ganador() is None:
            if self.__rondas >= MAX_RONDAS:
                self.__empate_por_rondas = True
                break

            self.__rondas += 1
            self._imprimir(f"\n--- Ronda {self.__rondas} ---")
            danio_ronda = 0

            for _ in range(2):
                atacante = self.atacante_actual
                objetivo = self.__participantes[1 - self.__turno]
                # Polimorfismo: no se pregunta de qué clase es el atacante.
                danio = atacante.atacar(objetivo)
                danio_ronda += danio
                self._imprimir(f"{atacante.nombre} ataca a {objetivo.nombre} y causa {danio} de daño.")
                self._imprimir(f"  {p1.mostrar_estado()}")
                self._imprimir(f"  {p2.mostrar_estado()}")
                if self.verificar_ganador() is not None:
                    break
                self.cambiar_turno()

            if self.verificar_ganador() is None and danio_ronda == 0:
                self.__empate_tecnico = True
                break

        self.mostrar_resultado()
        return self.verificar_ganador()

    def mostrar_resultado(self):
        ganador = self.verificar_ganador()
        if ganador is not None:
            self._imprimir(f"\nGanador: {ganador.nombre} (en {self.__rondas} rondas)")
        elif self.__empate_tecnico:
            self._imprimir("\nEmpate técnico: una ronda completa sin daño.")
        elif self.__empate_por_rondas:
            self._imprimir(f"\nEmpate: se completaron {MAX_RONDAS} rondas sin ganador.")
        else:
            self._imprimir("\nEl combate aún no ha terminado.")
