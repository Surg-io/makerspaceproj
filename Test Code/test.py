import liquidcrystal_i2c

cols = 20
rows = 4

lcd = liquidcrystal_i2c.LiquidCrystal_I2C(0x27, 1, numlines=rows)

lcd.printline(0, 'Initializing'.center(cols))
lcd.printline(1, 'Backend...'.center(cols))
lcd.printline(2, 'python-')
lcd.printline(3, 'liquidcrystal_i2c'.rjust(cols))
