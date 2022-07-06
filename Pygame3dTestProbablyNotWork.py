import math, pygame
RED = (200,0,0)
BLUE = (0,0,200)
GREEN = (0,200,0)
BLACK = (0,0,0)
LIGHT_BLUE = (100, 100, 255)
LIGHT_GREEN = (100, 255, 100)
LIGHT_RED = (255, 100, 100)
GRAY = (127, 127, 127)

class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    @staticmethod
    def times_magnitude(v, m):
        return Vector(v.x*m, v.y*m, v.z*m)
    @staticmethod
    def add(v,w):
        return Vector(v.x+w.x, v.y+w.y, v.z+w.z)
    @staticmethod
    def subtract(v, w):
        return Vector(v.x-w.x, v.y-w.y, v.z-w.z)
    @staticmethod 
    def pretty_string(v):
        return "(" + str(round(v.x*100)/100) + "," + str(round(v.y*100)/100) + "," + str(round(v.z*100)/100) + ")"

class Triangle:
    def __init__(self, p1, p2, p3, color):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.color = color
    def get_points_array(self):
        return (self.p1, self.p2, self.p3)
    def get_moved_triangle(self, p):
        return Triangle(Vector.add(self.p1,p), Vector.add(self.p2,p), Vector.add(self.p3,p), self.color)

# camera pos, forward vector, up vector, right vector, distance to screen, point
def OLD_get_screen_pos_of_global_point(c_pos, forward, up, right, FOV, p):
    # middle of screen plane position
    origo = Vector.add(Vector.times_magnitude(forward, FOV), c_pos)

    # plane
    p_A = forward.x
    p_B = forward.y
    p_C = forward.z
    p_D = - p_A*origo.x - p_B*origo.y - p_C*origo.z

    # line from C:camera to P:position
    l_start = c_pos # start pos
    l_v = Vector.subtract(p, c_pos) # vector of line

    # solve equation where you put coordinates of line into plane Ax+Bx+Cx+D=0 function
    t_part = p_A*l_v.x + p_B*l_v.y + p_C*l_v.z
    answer = - (p_A*l_start.x + p_B*l_start.y + p_C*l_start.z + p_D) / t_part

    # p', point where the line intersects the plane
    p_intersect = Vector.add(l_start, Vector.times_magnitude(l_v, answer))

    # convert p_intersect into coordinates on the plane: (a, b)
    point_b = 0
    point_a = 0
    if True or right.x != 0:
        point_b = (-p_intersect.x*right.y + p_intersect.y*right.x)/(-up.x*right.y + up.y*right.x)
        point_a = (p_intersect.x - point_b*up.x)/(right.x)
    return point_a, point_b
def get_screen_pos_of_global_point(C, f, u, r, FOV, p): # camera_pos, forward, up, right, FOV, point

    O = Vector.add(C , Vector.times_magnitude(f, FOV)) # origo

    D = - f.x*O.x - f.y*O.y - f.z*O.z

    # check if behind or in front of plane, by putting p coordinates into plane function Ax + By + Cz + D 
    if f.x*p.x + f.y*p.y + f.z*p.z + D  < 0:
        return 0, 0

    # line vector
    l_v = Vector.subtract(p, C)
    
    # p on plane = p_
    div = (f.x*l_v.x + f.y*l_v.y + f.z*l_v.z)
    if abs(div) < 0.001:
        return 0, 0
    t = (- f.x*C.x - f.y*C.y - f.z*C.z - D) / div
    p_ = Vector.add(C, Vector.times_magnitude(l_v, t))

    # (a, b) on plane where (0,0) is O
    # only works if u.x not 0
    if abs(r.z) > abs(u.x) and abs(r.z) > abs(r.x) and abs(r.z) > abs(u.z):
        b = (r.z*(p_.y - O.y) + r.y*(O.z - p_.z)) / (r.z*u.y - r.y*u.z)
        a = (p_.z - b*u.z - O.z) / r.z
    elif abs(u.z) > abs(r.x) and abs(u.z) > abs(u.x):
        a = (u.z*(p_.y - O.y) + u.y*(O.z - p_.z)) / (u.z*r.y - u.y*r.z)
        b = (p_.z - a*r.z - O.z) / u.z
    elif abs(r.x) > abs(u.x): 
        b = (r.x*(p_.y - O.y) + r.y*(-p_.x + O.x)) / (r.x*u.y - r.y*u.x)
        a = (p_.x - b*u.x - O.x) / r.x
    else:
        a = (u.x*(p_.y - O.y) + u.y*(-p_.x + O.x)) / (r.y*u.x - r.x*u.y) 
        b = (p_.x - a*r.x - O.x) / u.x
    return a, b

def rotate_around_y_axis(radians,f,u,r): # forward, up, right
    cosx = math.cos(radians)
    sinx = math.sin(radians)
    f.__init__(f.x*cosx - f.z*sinx, f.y, f.x*sinx + f.z*cosx)
    u.__init__(u.x*cosx - u.z*sinx, u.y, u.x*sinx + u.z*cosx)
    r.__init__(r.x*cosx - r.z*sinx, r.y, r.x*sinx + r.z*cosx)
def rotate_around_z_axis(radians, f, u, r):
    cosx = math.cos(radians)
    sinx = math.sin(radians)
    f.__init__(f.x*cosx + f.y*sinx, -f.x*sinx + f.y*cosx, f.z)
    u.__init__(u.x*cosx + u.y*sinx, -u.x*sinx + u.y*cosx, u.z)
    r.__init__(r.x*cosx + r.y*sinx, -r.x*sinx + r.y*cosx, r.z)

class Game:
    def __init__(self):
        self.width = 700
        self.height = 700
        self.screen = pygame.display.set_mode([self.width, self.height])
        self.cam = Camera()
        
        self.clock = pygame.time.Clock()
        self.framerate = 60
        self.frame_time = 0 # time for last frame to take place

        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)
        self.mouse_move = (0,0)

        self.font = pygame.font.Font(None, 20)

        self.game_objects = [Cuboid_Obj(Vector(-50,100,50),100, 100, -200, RED),
                             Cuboid_Obj(Vector(100, 30, -50), 50, 50, 50, RED)]

        self.start_game()

    def start_game(self):
        running = True
        while running:
            pygame.mouse.set_pos((300,300))
            self.mouse_move = (0,0)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEMOTION:
                    self.mouse_move = event.rel
                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_SPACE: # place stuff

                        self.game_objects.append(Cuboid_Obj(self.cam.pos, 50,50,50, GREEN))

                    elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        running = False

            self.game_logic()
            self.draw_game()

            # Flip the display
            pygame.display.flip()

            self.frame_time = self.clock.tick(self.framerate)

    def game_logic(self):
        self.cam.logic(self)
        
    def draw_game(self):
        self.cam.draw(self)

class Camera:
    def __init__(self):
        self.FOV = 0.5
        self.pos = Vector(0,0,0)
        self.forward = Vector(1,0,0) # unit vectors with length 1
        self.up = Vector(0,1,0)
        self.right = Vector(0,0,1)

        self.rotation_around_y = 0.0001
        self.rotation_around_z = 0.0001
    def logic(self, g):
        pressed_keys = pygame.key.get_pressed()

        # reset view vectors
        self.forward = Vector(1,0,0) # unit vectors with length 1
        self.up = Vector(0,1,0)
        self.right = Vector(0,0,1)
        
        # change rotation
        rotation_speed = 0.001
        self.rotation_around_y += g.mouse_move[0] * rotation_speed
        self.rotation_around_z -= g.mouse_move[1] * rotation_speed

        # rotate unit vectors (in right order, first around z, then y)
        rotate_around_z_axis(self.rotation_around_z, self.forward, self.up, self.right)
        rotate_around_y_axis(self.rotation_around_y, self.forward, self.up, self.right)
        
        # move
        speed = 1.001
        if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:
            self.pos = Vector.add(self.pos, Vector.times_magnitude(self.right,speed))
        if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:
            self.pos = Vector.add(self.pos, Vector.times_magnitude(self.right,-speed))
        if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_w]: # forward
            self.pos = Vector.add(self.pos, Vector.times_magnitude(self.forward,speed))
        if pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_s]: # forward
            self.pos = Vector.add(self.pos, Vector.times_magnitude(self.forward,-speed))
        if pressed_keys[pygame.K_SPACE]:
            self.pos.y -= speed

    def draw(self, g):
        g.screen.fill((255, 255, 255))

        # sort triangles based on distance to camera
        def distance_to_camera(t):
            return -(pow(((t.p1.x + t.p2.x + t.p3.x)/3) - self.pos.x, 2) + pow(((t.p1.y + t.p2.y + t.p3.y)/3) - self.pos.y, 2) + pow(((t.p1.z + t.p2.z + t.p3.z)/3) - self.pos.z, 2))
        triangles = []
        for game_object in g.game_objects:
            for triangle in game_object.triangles:
                triangles.append(triangle.get_moved_triangle(game_object.pos))
        triangles = sorted(triangles, key=lambda x: distance_to_camera(x))
        
        # draw triangles
        for triangle in triangles:
            points = [(0,0),(0,0),(0,0)]
            for i, point in enumerate(triangle.get_points_array()):
                x, y = get_screen_pos_of_global_point(self.pos, self.forward, self.up, self.right, self.FOV, point)

                if x == 0 and y == 0: break
                
                x *= g.width
                y *= g.height

                x += g.width/2
                y += g.height/2

                points[i] = (int(x), int(y))
            else: # success
                pygame.draw.polygon(g.screen, triangle.color, points)

        # draw text
        texts = ["Forward: " + Vector.pretty_string(self.forward),"Up: " + Vector.pretty_string(self.up),
                 "Right: " + Vector.pretty_string(self.right),"Position: " + Vector.pretty_string(self.pos)]
        for i, text in enumerate(texts):
            text_surface = g.font.render(text, True, (0,0,0))
            g.screen.blit(text_surface, (0,i*20))

class GameObject: # consists of a position and some triangles
    def __init__(self, pos, triangles):
        self.pos = pos
        self.triangles = triangles

class Cuboid_Obj(GameObject):
    def __init__(self, pos, length, height, width, color):
        triangles = [Triangle(Vector(0,0,0),Vector(length,0,0),Vector(0,height,0), LIGHT_BLUE), # x y face on back
                     Triangle(Vector(0,height,0),Vector(length,0,0),Vector(length,height,0), LIGHT_BLUE),
                     Triangle(Vector(0,0,width),Vector(length,0,width),Vector(0,height,width), BLUE), # moved to front
                     Triangle(Vector(0,height,width),Vector(length,0,width),Vector(length,height,width), BLUE),

                     Triangle(Vector(0,0,0),Vector(length,0,0),Vector(0,0,width), RED), # x z face on top
                     Triangle(Vector(0,0,width),Vector(length,0,width),Vector(length,0,0), RED),
                     Triangle(Vector(0,height,0),Vector(length,height,0),Vector(0,height,width), LIGHT_RED), # moved to bottom
                     Triangle(Vector(0,height,width),Vector(length,height,width),Vector(length,height,0), LIGHT_RED),
                     
                     Triangle(Vector(0,0,0),Vector(0,0,width),Vector(0,height,0), GREEN), # y z face on left side
                     Triangle(Vector(0,0,width),Vector(0,height,width),Vector(0,height,0), GREEN),
                     Triangle(Vector(length,0,0),Vector(length,0,width),Vector(length,height,0), LIGHT_GREEN), # moved to right
                     Triangle(Vector(length,0,width),Vector(length,height,width),Vector(length,height,0), LIGHT_GREEN)]

        super().__init__(pos, triangles)

def main():
    pygame.init()
    game = Game()
    pygame.quit()

if __name__ == "__main__":
    main()



    
    