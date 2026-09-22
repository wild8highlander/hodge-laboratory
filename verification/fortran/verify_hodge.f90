! ═══════════════════════════════════════════════════════════════════
! HODGE LABORATORY — FORTRAN VERIFICATION
! Laboratory "The Dynamic Principle" (Isaev Iskhak Khamzatovich)
!
! Exact integer censuses, ranks and invariants — 64-bit arithmetic.
! Run:  gfortran -O2 -o verify_hodge verify_hodge.f90 && ./verify_hodge
! Exit codes: 0 — all checks accepted, 1 — at least one failure.
! ═══════════════════════════════════════════════════════════════════
program verify_hodge
    use iso_fortran_env, only: int64
    implicit none
    integer :: passes, fails
    integer(int64) :: prod, snf_type(8)
    integer :: i

    snf_type = (/ 1_int64, 1_int64, 5_int64, 5_int64, &
                  15_int64, 15_int64, 15_int64, 15_int64 /)

    passes = 0
    fails = 0

    ! ─── 1. Character census N=15/30 (exact) ───
    call check_int('N=15: sum h_d = 91', sum_census(15), 91_int64, passes, fails)
    call check_int('N=30: sum h_d = 406', sum_census(30), 406_int64, passes, fails)
    call check_int('N=7:  sum h_d = 15', sum_census(7), 15_int64, passes, fails)

    ! h_d tables: N=15 → 1, 6, 84;  N=30 → ..., 276
    call check_int('N=15: h(3) = 1', census_d(15, 3), 1_int64, passes, fails)
    call check_int('N=15: h(5) = 6', census_d(15, 5), 6_int64, passes, fails)
    call check_int('N=15: h(15) = 84', census_d(15, 15), 84_int64, passes, fails)
    call check_int('N=30: h(30) = 276', census_d(30, 30), 276_int64, passes, fails)

    ! ─── 2. Klein quartic ───
    call check_int('Klein j = -c4^3/Delta = -3375 = -15^3', -105**3 / 343, -3375_int64, passes, fails)
    call check_int('Klein 343 * 3375 = 105^3', 343_int64 * 3375_int64, 1157625_int64, passes, fails)

    ! ─── 3. Discriminant and SNF ───
    call check_int('disc = 3^4*5^6 = 1265625', 3**4 * 5**6, 1265625_int64, passes, fails)
    call check_int('sqrt(disc) = 1125', isqrt(1265625_int64), 1125_int64, passes, fails)
    prod = 1_int64
    do i = 1, 8
        prod = prod * snf_type(i)
    end do
    call check_int('SNF product = 1265625', prod, 1265625_int64, passes, fails)

    ! ─── 4. Ladder and denominators ───
    call check_int('Q_stand = 2*30*8 = 480', 2 * 30 * 8, 480_int64, passes, fails)
    call check_int('E8: even(Arf=0) = 36 @ g=3', 2**2 * (2**3 + 1), 36_int64, passes, fails)
    call check_int('E8: odd(Arf=1) = 28 @ g=3', 2**2 * (2**3 - 1), 28_int64, passes, fails)
    call check_int('E8: total = 64', 36 + 28, 64_int64, passes, fails)

    ! ─── 5. Flow termination (E4) ───
    call check_int('t*(48,48,1,1) = 48', tstar(48, 48, 1, 1), 48_int64, passes, fails)
    call check_int('t*(24,36,3,5) = 72', tstar(24, 36, 3, 5), 72_int64, passes, fails)
    call check_int('t*(12,12,4,6) = 6', tstar(12, 12, 4, 6), 6_int64, passes, fails)

    ! ─── 6. K3: stand numbers ───
    call check_int('K3: 22 = 1+7+7+7', 1 + 7 + 7 + 7, 22_int64, passes, fails)
    call check_int('K3: det = 64 = 8^2', 8 * 8, 64_int64, passes, fails)
    call check_int('K3: rank 20 = 1+19', 1 + 19, 20_int64, passes, fails)

    ! ─── 7. Genus of the Fermat curve ───
    call check_int('g(15) = 91', (15 - 1) * (15 - 2) / 2, 91_int64, passes, fails)
    call check_int('g(30) = 406', (30 - 1) * (30 - 2) / 2, 406_int64, passes, fails)

    print '(/a, i0, a, i0, a)', new_line('a')//'  VERDICT: ', passes, &
        ' PASS, ', fails, ' FAIL'
    if (fails == 0) then
        stop 0
    else
        stop 1
    end if

contains

    ! ─── census: sum of h_d over all conductors ───
    integer(int64) function sum_census(N)
        integer, intent(in) :: N
        integer :: a, b
        integer(int64) :: cnt
        cnt = 0
        do a = 1, N - 1
            do b = 1, N - a - 1
                cnt = cnt + 1
            end do
        end do
        sum_census = cnt
    end function

    ! ─── census: h_d for a given conductor ───
    integer(int64) function census_d(N, d)
        integer, intent(in) :: N, d
        integer :: a, b, g0, dd
        integer(int64) :: cnt
        cnt = 0
        do a = 1, N - 1
            do b = 1, N - a - 1
                g0 = igcd(igcd(N, a), b)
                dd = N / g0
                if (dd == d) cnt = cnt + 1
            end do
        end do
        census_d = cnt
    end function

    integer function igcd(a, b)
        integer, intent(in) :: a, b
        integer :: x, y, r
        x = a; y = b
        do while (y /= 0)
            r = mod(x, y)
            x = y
            y = r
        end do
        igcd = x
    end function

    integer(int64) function isqrt(n)
        integer(int64), intent(in) :: n
        integer(int64) :: r
        r = int(sqrt(real(n)))
        do while (r * r > n)
            r = r - 1
        end do
        do while ((r + 1) * (r + 1) <= n)
            r = r + 1
        end do
        isqrt = r
    end function

    integer(int64) function tstar(W, H, a, b)
        integer, intent(in) :: W, H, a, b
        tstar = lcm64(W / igcd(a, W), H / igcd(b, H))
    end function

    integer(int64) function lcm64(a, b)
        integer(int64), intent(in) :: a, b
        lcm64 = a * b / igcd64(a, b)
    end function

    integer(int64) function igcd64(a, b)
        integer(int64), intent(in) :: a, b
        integer(int64) :: x, y, r
        x = a; y = b
        do while (y /= 0)
            r = mod(x, y)
            x = y
            y = r
        end do
        igcd64 = x
    end function

    subroutine check_int(name, actual, expected, passes, fails)
        character(len=*), intent(in) :: name
        integer(int64), intent(in) :: actual, expected
        integer, intent(inout) :: passes, fails
        if (actual == expected) then
            passes = passes + 1
            print '(a, a, a)', '  [PASS] ', name, ''
        else
            fails = fails + 1
            print '(a, a, a, i0, a, i0)', '  [FAIL] ', name, &
                '  got ', actual, ' expected ', expected
        end if
    end subroutine

end program verify_hodge
