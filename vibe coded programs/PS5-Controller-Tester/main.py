import pygame
import sys

pygame.init()
pygame.joystick.init()

screen = pygame.display.set_mode((500, 300))
pygame.display.set_caption("Joystick Button Tester")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 22)

joysticks = {}

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.JOYDEVICEADDED:
            joy = pygame.joystick.Joystick(event.device_index)
            joysticks[joy.get_instance_id()] = joy
            print(f"Connected: {joy.get_name()}")
        elif event.type == pygame.JOYDEVICEREMOVED:
            del joysticks[event.instance_id]
        elif event.type == pygame.JOYBUTTONDOWN:
            print(f"BUTTON DOWN: {event.button}")
        elif event.type == pygame.JOYBUTTONUP:
            print(f"BUTTON UP: {event.button}")
        elif event.type == pygame.JOYAXISMOTION:
            if abs(event.value) > 0.5:
                print(f"AXIS {event.axis}: {event.value:.2f}")
        elif event.type == pygame.JOYHATMOTION:
            print(f"HAT {event.hat}: {event.value}")

    screen.fill((20, 20, 20))
    y = 10
    if not joysticks:
        screen.blit(font.render("No controller detected", True, (255, 80, 80)), (10, y))
    else:
        for jid, joy in joysticks.items():
            screen.blit(font.render(f"{joy.get_name()}", True, (255, 255, 255)), (10, y))
            y += 30
            screen.blit(font.render("Press buttons/move sticks - check console", True, (180, 180, 180)), (10, y))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()