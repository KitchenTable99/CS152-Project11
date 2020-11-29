# Bruce A. Maxwell
# CS 151S
# Fall 2015
#
# Project 9
# Collision handler
#
# modified slightly by Eric Aaron for CS 152, Spring '19
# updated by Bruce Maxwell for CS 152, Fall 2019
#   fixed an issue in ball-block collision that would return False when the ball was inside the block
#   updated the ball-ball collisions to use the proper ray-circle intersections
# updated by Bruce Maxwell Spring 2020
#   updated the ball-block collision to handle a bug when tmax == 0.0
#   updated to incorporate bound/not bounce parameter
#   updated to incorporate last side hit function
#   updated to use positional arguments to Block (instructions in project page)
#   updated to no longer use any fields of the Block object
#

# Three API functions

# collision_ball_ball( ball1, ball2, dt, bounce=True )
# '''tests if ball1 collides with ball2 within time dt, assuming ball2 is stationary
#
#    if bounce is True, ball1 and ball2 will reflect their velocities
#    around the normal to the collision point.
#
#    If bounce is False, the velocities of ball1 and ball2 will not be
#    modified.
#
#    ball1's motion will be continued through the time period dt,
#    including after the collision
#
#    ball2's motion will not be updated'''

# collision_ball_block( ball, block, dt, bounce=True )
# '''tests if ball collides with block within time dt, assuming block is stationary
#
#    if bounce is True, ball1 will reflect its velocity around the normal to
#    the collision point. The block's velocity is not affected.
#
#    if bounce is False, the velocity of ball will not be modified
#
#    ball's motion will be continued through the time period dt,
#    including after the collision
#
#    block's motion will not be updated'''
#

# getBlockSideHit()
# '''returns which side of the block was most recently hit the last time
#    collision_ball_block was called
#
#    0: hit on left side
#    1: hit on right side
#    2: hit on top side
#    3: hit on bottom side
#
#    if there was no collision the last time ball_block was called, the
#    value is undefined (not meaningful)

import physics_objects as pho
import math
import graphicsPlus as gr

# module global variable indicating the side on which the last block was hit
__last_block_side_hit = None

# returns which side of the block was last hit
    # -1: no collision
    # 0: coming from the left, hit on left side
    # 1: coming from the right, hit on right side
    # 2: coming down from above, hit on top side
    # 3: coming up from below, hit on bottom side
def getBlockSideHit():
    return __last_block_side_hit

def length(v):
    """utility math function for calculating Euclidean length of a 2D vector"""
    return math.sqrt(v[0]*v[0] + v[1]*v[1])

def unit(v):
    """utility math function for creating a unit 2D vector"""
    l = math.sqrt(v[0]*v[0] + v[1]*v[1])
    if l > 0.0:
        return (v[0]/l, v[1]/l)
    return v



def collisionTest_ball_ball(ball1, ball2):
    """Tests if there is a collision with another ball along the path of
    the ball.  Returns the distance to the collision or 1e+6 (a big number)"""
    
    # Concept: hold ball2 still and test if ball1 will hit it
    # Ray-circle intersection
    v1 = ball1.getVelocity()
    p1 = ball1.getPosition()
    p2 = ball2.getPosition()
    r = ball1.getRadius() + ball2.getRadius()

    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]

    # quadratic equation
    a = v1[0]*v1[0] + v1[1]*v1[1]
    b = dx*v1[0] + dy*v1[1]
    c = dx*dx + dy*dy - r*r

    delta = b*b - a*c
    
    if  delta <= 0: # no intersection, imaginary roots
        return 1e+6

    deltaroot = math.sqrt(delta)
    t1 = (-b + deltaroot) / a
    t2 = (-b - deltaroot) / a

    if t1 < 0 and t2 < 0: # intersection is behind the ball
        return 1e+6

    # one of these could be negative
    tmin = min(t1, t2)

    # ball's already intersect, so move ball1 back to the boundary
    if t1 < 0 or t2 < 0:
        newpx = p1[0] + tmin*v1[0]
        newpy = p1[1] + tmin*v1[1]
        ball1.setPosition( [newpx, newpy] )
        return 0.0
        
    dx = tmin*v1[0]
    dy = tmin*v1[1]
    distToImpact = math.sqrt(dx*dx + dy*dy)

    return distToImpact
    

def collision_ball_ball(ball1, ball2, dt, bounce=True):
    """Main collision function for handling ball/ball collisions
    Updates the ball1's position and returns true if there was a collision.
    Returns False if there was no collision (ball1 still needs to be udpated).
    ball2's velocity is changed, but it is not updated by this function"""

    # holds ball2 steady, tests ball1's trajectory
    distToImpact = collisionTest_ball_ball(ball1, ball2)

    # get the magnitude of the velocity of ball1
    v1 = ball1.getVelocity()
    v2 = ball2.getVelocity()
    vmag1 = length( ball1.getVelocity() )

    # no collision if it's too far away
    if distToImpact > vmag1 * dt:
        return False

    # check for a stationary ball
    if vmag1 < 1e-6:
        # just update and return a collision
        ball1.update( dt )
        return True

    delta = distToImpact / (vmag1*dt)

    # don't update backwards, which can happen, strangely enough
    if delta > 0.0:
        ball1.update( delta*dt )

    # if we want ball1 and ball2 to bounce
    if bounce:
        p1 = ball1.getPosition()
        p2 = ball2.getPosition()
        rvec = unit( (p1[0] - p2[0], p1[1] - p2[1]) ) # reflection vector

        # create the reflection matrix R(th)M(X)R(-th)

        # update ball1's velocity
        # rotate reflection vector to the Y axis
        tvx =  rvec[0] * v1[0] + rvec[1] * v1[1]
        tvy = -rvec[1] * v1[0] + rvec[0] * v1[1]

        # mirror in X
        tvx = - tvx*ball1.getElasticity()*ball2.getElasticity() # need to add the loss factor here

        # rotate back
        vfx = rvec[0] * tvx - rvec[1] * tvy
        vfy = rvec[1] * tvx + rvec[0] * tvy

        ball1.setVelocity( [vfx, vfy] )

        # update ball2's velocity
        tvx =  rvec[0] * v2[0] + rvec[1] * v2[1]
        tvy = -rvec[1] * v2[0] + rvec[0] * v2[1]

        # mirror in X
        tvx = - tvx*ball1.getElasticity()*ball2.getElasticity() # need to add the loss factor here

        # rotate back
        vfx = rvec[0] * tvx - rvec[1] * tvy
        vfy = rvec[1] * tvx + rvec[0] * tvy

        ball2.setVelocity( [vfx, vfy] )

    # finish updating ball1
    if delta > 0.0:
        ball1.update( dt - delta*dt )
    else:
        ball1.update( dt )

    return True


def collisionTest_ball_block(ball, block):
    """Test if a ball is colliding with any side of a block, and indicate
    which side. Sends out a line along the ball's velocity vector and
    compares it with all four sides of the object."""

    # get the trajectory and position of the ball
    v = unit( ball.getVelocity() )
    ballP = ball.getPosition()
    radius = ball.getRadius()

    # get the position of the block
    blockP = block.getPosition()

    # a variation on Liang-Barsky clipping
    # expands the block by the size of the ball before testing
    dx = block.getWidth()
    dy = block.getHeight()

    p = ( -v[0], v[0], -v[1], v[1] )
    q = (ballP[0] - (blockP[0] - dx*0.5 - radius),
         (blockP[0] + dx*0.5 + radius) - ballP[0],
         ballP[1] - (blockP[1] - dy*0.5 - radius),
         (blockP[1] + dy*0.5 + radius) - ballP[1] )


    # for all four cases
    tmin = -1e+6
    tmax = 1e+6
    side = -1
    sidemax = -1
    for i in range(4):
        if p[i] == 0.0: # no collision for this side of the block, motion is parallel to it
            if q[i] < 0: # outside the boundary of the box, no collision
                return 1e+6,0
            continue

        tk = q[i] / p[i]

        if p[i] < 0: # outside moving in
            if tk > tmin:
                tmin = tk
                side = i
        else:
            if tk < tmax:
                tmax = tk
                sidemax = i

        if tmax <= tmin: # no intersection with the box
            return 1e+6,0

    if tmin < 0 and tmax <= 0: # both intersections behind the ball
        tmin = 1e+6
    elif tmin < 0 and tmax > 0: # ball is intersecting the block

        # move the ball back along its velocity to the intersection point
        if v[0] == 0.0 and v[1] == 0.0:
            v = (1.0, 0.0)
            tmin = (blockP[0] - 0.5*dx - radius) - ballP[0]

        # move it to the closest side and set distance to impact to 0
        if -tmin < tmax:
            ball.setPosition( [ballP[0] + (tmin+1e-3)*v[0], ballP[1] + (tmin+1e-3)*v[1]] )
        else:
            ball.setPosition( [ballP[0] + (tmax+1e-3)*v[0], ballP[1] + (tmax+1e-3)*v[1]] )
        tmin = 0


    # tmin is the closest intersection on side i
    # 0: coming from the left
    # 1: coming from the right
    # 2: coming up from below
    # 3: coming down from above
    return (tmin, side)


def collision_ball_block(ball, block, dt, bounce=True):
    """Main collision code for ball/block interactions.
    Updates the ball's position and returns true if there was a collision.
    Returns False if there was no collision (ball still needs to be udpated).
    Does not update or modify the block."""

    # get distance to impact
    distToImpact, side = collisionTest_ball_block( ball, block )
    
    global __last_block_side_hit
    __last_block_side_hit = side

    # check if the impact is farther away than one step
    vmag = length( ball.getVelocity() )
    if vmag == 0.0 or distToImpact > vmag * dt:
        return False

    
    # update the ball prior to the collision
    delta = distToImpact / (vmag * dt)
    ball.update( delta * dt )

    if bounce:
        # modify the velocities
        v = ball.getVelocity()
        if side == 0 or side == 1: # left or right wall, so adjust x
            ball.setVelocity( [-v[0]*ball.getElasticity()*block.getElasticity(), v[1]]  )
        elif side == 2 or side == 3: # top or bottom wall, so adjust y
            ball.setVelocity( [v[0], -v[1]*ball.getElasticity()*block.getElasticity()]  )

    # update the ball post-collision
    ball.update( (1 - delta) * dt )

    return True


# Main collision code for a ball and a rotated block
# Updates the ball's position and returns true if there was a collision.
# Returns False if there was no collision (ball still needs to be updated).
def collision_ball_rotating_block(ball, block, dt, bounce=True):

    # transform the ball the same way by subtracting the center of the
    # original block and rotating it to the same alignment (use anchor point?)
    p0 = ball.getPosition()
    bp = block.getPosition()
    b0 = block.getAOR()
    blockwidth = block.getWidth()
    blockheight = block.getHeight()
    
    # we have the 0-angle state of the block so create a faux block so the anchor is at 0, 0
    # ***** uses positions of first four
    fauxBlock = pho.Block( gr.Point(bp[0] - b0[0], bp[1] - b0[1] ), blockwidth, blockheight )

    # rotate the ball's velocity
    v0 = ball.getVelocity()

    theta = math.pi * block.getTheta() / math.radians(180)
    cth = math.cos( theta )
    sth = math.sin( theta )
    vtx =  v0[0] * cth + v0[1] * sth
    vty = -v0[0] * sth + v0[1] * cth

    px = p0[0] - b0[0]
    py = p0[1] - b0[1]
    pxx =  px * cth + py * sth
    pyy = -px * sth + py * cth

    ball.setPosition([pxx, pyy])
    ball.setVelocity([vtx, vty])

    # test if there is a collision
    distToImpact, side = collisionTest_ball_block( ball, fauxBlock )

    if distToImpact < 0: # back up the ball, and there was a collision
        distToImpact = 0.0

    # set the ball back to its original position
    ball.setPosition([p0[0],p0[1]])
    ball.setVelocity([v0[0],v0[1]])
            
    acc = ball.getAcceleration()
    tvx = v0[0] + acc[0] * dt
    tvy = v0[1] + acc[1] * dt
    vmag = length( (tvx, tvy) )

    if distToImpact > 0.0 and vmag == 0.0 or distToImpact > vmag * dt:
        return False

    global __last_block_side_hit
    __last_block_side_hit = side

    # if there was a collision, update the ball to the collision point
    # set the ball back to its original velocity and update
    distToImpact = min(0.0, distToImpact)
    delta = distToImpact / vmag 
    ball.update( delta )
    
    # if there was a collision, re-align the new velocity with the block
    v0 = ball.getVelocity()

    # convert velocities to the collision space
    vtx =  v0[0] * cth + v0[1] * sth
    vty = -v0[0] * sth + v0[1] * cth

    # need to give it a boost or a sink if the block is rotating based on the moment arm from the center of rotation
    dx = pxx # transformed distance between anchor and the ball
    dy = pyy 
    dist = length( (dx, dy) )
    rotvel = math.pi * block.getOmega() / math.radians(180.)
    linvel = dist*2.*math.pi * rotvel / (2. * math.pi)

    if side == 0: # left side of the block, so x velocity has to be negative
        vtx = math.copysign(vtx * ball.getElasticity()*block.getElasticity(), -1)
        hsin = dy/dist # length of the moment arm hitting the ball
        velmod = -hsin * linvel # modify the linear velocity
        #print 'left:', hsin, linvel, vtx, velmod, vtx + velmod 
        vtx += velmod

    elif side == 1: # right side of the block
        vtx = math.copysign(vtx * ball.getElasticity()*block.getElasticity(), 1)
        hsin = dy/dist # length of the moment arm hitting the ball
        velmod = -hsin * linvel # modify the linear velocity
        #print 'right:', hsin, linvel, vtx, velmod, vtx + velmod 
        vtx += velmod
        
    elif side == 2: # bottom side
        vty = math.copysign(vty * ball.getElasticity()*block.getElasticity(), -1)
        hsin = dx/dist
        velmod = hsin * linvel
        #print 'bottom:', hsin, linvel, vty, velmod, vty + velmod 
        vty += velmod

    else: # top side
        vty = math.copysign(vty * ball.getElasticity()*block.getElasticity(), 1)
        hsin = dx/dist
        velmod = hsin * linvel
        #print 'top:', hsin, linvel, vty, velmod, vty + velmod 
        vty += velmod
        
    # rotate the velocity back
    vttx = vtx * cth - vty * sth
    vtty = vtx * sth + vty * cth

    if bounce:
        ball.setVelocity([vttx, vtty])

    ball.update( (1 - delta) * dt )

    return True

def collision_ball_shitty_snowman(ball, snowman, dt, bounce=True):
    for body_part in snowman.getBodyParts():
        collision_ball_ball(ball, body_part, dt, bounce)



###### collision_router and helper functions go here  ################
collision_router = {}
collision_router[('Ball', 'Ball')] = collision_ball_ball
collision_router[('Ball', 'Block')] = collision_ball_block
collision_router[('Ball', 'Triangle')] = collision_ball_ball
collision_router[('Ball', 'Shitty Snowman')] = collision_ball_shitty_snowman
collision_router[('Ball', 'Rotating Block')] = collision_ball_rotating_block


def collision(ball, thing, dt, bounce=True):
    key = (ball.getType(), thing.getType())
    return collision_router[key](ball, thing, dt, bounce)
